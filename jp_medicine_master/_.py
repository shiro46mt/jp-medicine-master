from logging import getLogger
import os
from pathlib import Path
from typing import Union, Optional, List, Dict
import zipfile

from bs4 import BeautifulSoup
import pandas as pd
import requests

# ログ設定
logger = getLogger(__name__)

# ファイル保存元URL
def get_url_ssk(year: Optional[int] = None, *, verbose: bool = False) -> Union[str, Dict[int, str]]:
    """支払基金HPで公開されている医薬品マスタの、提供ページのリンクurlを返す。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        verbose: Trueを指定した場合、リンクの一覧をdictとして返す。
    """
    urls = {
        2024: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r06/kihonmasta_04.html",
        2022: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r04/kihonmasta_04.html",
        2020: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r02/kihonmasta_04.html",
        2019: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r01/kihonmasta_04.html",  # 2019-10-01から適用
        2018: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/h30/kihonmasta_04.html",
        2016: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/h28/kihonmasta_04.html",
        2014: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/h26/kihonmasta_04.html",
        2012: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/h24/kihonmasta_04.html",
    }
    if verbose:
        return urls
    if year:
        if year not in urls:
            raise ValueError(f"{year} is not a valid value for year; supported values are {', '.join(urls.keys())}")
        if year == 2019:
            logger.warning('`year=2019` の医薬品マスタは、2019年10月の消費税率引上げによる改定後のマスタです。2019年9月までのマスタは `year=2018` を参照してください。')
        return urls[year]
    else:
        year = max(urls)
        return urls[year]


def get_url_mhlw(year: Optional[int] = None, *, verbose: bool = False) -> Union[str, Dict[int, str]]:
    """厚労省HPで公開されている医薬品マスタの、提供ページのリンクurlを返す。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        verbose: Trueを指定した場合、リンクの一覧をdictとして返す。
    """
    urls = {
        2024: "https://www.mhlw.go.jp/topics/2024/04/tp20240401-01.html",
        2023: "https://www.mhlw.go.jp/topics/2023/04/tp20230401-01.html",
        2022: "https://www.mhlw.go.jp/topics/2022/04/tp20220401-01.html",
        2021: "https://www.mhlw.go.jp/topics/2021/04/tp20210401-01.html",
        2020: "https://www.mhlw.go.jp/topics/2020/04/tp20200401-01.html",
        2019: "https://www.mhlw.go.jp/topics/2019/08/tp20190819-01.html",  # 2019-10-01から適用
        2018: "https://www.mhlw.go.jp/topics/2018/04/tp20180401-01.html",
        2016: "https://www.mhlw.go.jp/topics/2016/04/tp20160401-01.html",
    }
    if verbose:
        return urls
    if year:
        if year not in urls:
            raise ValueError(f"{year} is not a valid value for year; supported values are {', '.join(urls.keys())}")
        if year == 2019:
            logger.warning('`year=2019` の医薬品マスタは、2019年10月の消費税率引上げによる改定後のマスタです。2019年9月までのマスタは `year=2018` を参照してください。')
        return urls[year]
    else:
        year = max(urls)
        return urls[year]


class _MedicineMaster:
    # requests用パラメータ
    headers = {'User-Agent': ''}
    timeout_sec = 60

    @classmethod
    def get(self, url: str) -> BeautifulSoup:
        """urlへのHTTPアクセス"""
        html = requests.get(url, timeout=self.timeout_sec, headers=self.headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup

    @classmethod
    def fetch_file(self, download_url: str, save_dir: Union[str, os.PathLike], *, delete_tmp=True) -> Path:
        """download_urlのファイルをダウンロード -> zipの場合は解凍 -> ファイルを保存 -> ファイルパスを返す"""
        # 保存先フォルダ
        if isinstance(save_dir, str):
            save_dir = Path(save_dir)

        if not isinstance(save_dir, Path) or not save_dir.is_dir():
            raise FileNotFoundError("No such directory: '%s'", save_dir)

        # ダウンロードファイルの名前
        filename = download_url.split('/')[-1]
        filepath = save_dir / filename

        # ファイルダウンロード
        r = requests.get(download_url, stream=True)
        logger.info(f"Downloading from '{download_url}'")
        with open(filepath, 'wb') as zf:
            zf.write(r.content)

        # 拡張子が.zipでない場合は終了
        if filepath.suffix != '.zip':
            return filepath

        # zip解凍
        files = []
        with zipfile.ZipFile(filepath, 'r') as zf:
            for info in zf.infolist():
                info.filename = info.orig_filename.encode('cp437').decode('cp932')
                if os.sep != "/" and os.sep in info.filename:
                    info.filename = info.filename.replace(os.sep, "/")
                tmp = zf.extract(info, save_dir)
                files.append(Path(tmp))
        # zip削除
        if delete_tmp:
            filepath.unlink()

        return files[0]

    @classmethod
    def read(self, download_func, year: Optional[int] = None, save_dir: Union[str, os.PathLike, None] = None, numeric_cols: List[str] = []):
        """対象ファイルをホームディレクトリにダウンロード -> pandas.DataFrameとして読み込み -> ダウンロードファイルを削除"""
        # 保存先フォルダ
        if save_dir is None:
            save_dir = Path.home() / '.jp_medicine_master'
            if not save_dir.is_dir():
                save_dir.mkdir()
            delete_csv = True

        # 対象ファイルのダウンロード
        filepath = download_func(save_dir, year=year, delete_tmp=True)

        # 読み込み
        df = pd.read_csv(filepath, dtype=str, encoding='utf8')
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        # ダウンロードファイルの削除
        if delete_csv:
            Path(filepath).unlink()

        return df


#
# 支払基金 (ssk_y)
#
def download_ssk_y(save_dir: Union[str, os.PathLike], *, year: Optional[int] = None, delete_tmp=True) -> str:
    """支払基金HPから、医薬品マスターの一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        year: マスタの公開年度。指定しない場合は最新年度。
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.zip) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    url = get_url_ssk(year=year)
    soup = _MedicineMaster.get(url)

    link = soup.select_one('.table01').find('a')
    base_url = '/'.join(url.split('/')[:-1])
    download_url = base_url + '/' + link.attrs['href']

    # ファイルの保存
    filepath = _MedicineMaster.fetch_file(download_url, save_dir, delete_tmp=delete_tmp)

    # ヘッダ行の追加
    filepath_header = Path(__file__).parent / 'ssk_y_header.csv'
    df1 = pd.read_csv(filepath_header, dtype=str, encoding='utf8')
    cols = df1.columns
    df2 = pd.read_csv(filepath, dtype=str, encoding='cp932', names=cols)
    df2.to_csv(filepath, index=False, encoding='utf8')

    return str(filepath)


def read_ssk_y(*, year: Optional[int] = None, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """支払基金HPから、医薬品マスターを取得する。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        save_dir: 指定した場合、取得したマスタを `save_dir`にcsv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    return _MedicineMaster.read(download_ssk_y, year=year, save_dir=save_dir, numeric_cols=['医薬品名・規格名漢字有効桁数', '医薬品名・規格名カナ有効桁数', '単位漢字有効桁数', '新又は現金額', '旧金額'])


#
# 厚労省 薬価 (mhlw_price)
#
def download_mhlw_price(save_dir: Union[str, os.PathLike], *, year: Optional[int] = None, delete_tmp=True) -> str:
    """厚労省HPから、(1)-(4)薬価基準収載品目リストの一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        year: マスタの公開年度。指定しない場合は最新年度。
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.xlsx) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    url = get_url_mhlw(year=year)
    soup = _MedicineMaster.get(url)

    links = soup.select('#contents .ico-excel a')
    base_url = 'https://www.mhlw.go.jp'
    download_urls = [base_url + '/' + link.attrs['href'] for link in links[:4]]

    # ファイルの保存
    files = []
    for download_url in download_urls:
        filepath = _MedicineMaster.fetch_file(download_url, save_dir)
        files.append(filepath)

    # ファイルの結合
    df = pd.concat([
        pd.read_excel(filepath, dtype=str) for filepath in files
    ])
    df = df.rename(columns={'Unnamed: 4': '日本薬局方', 'Unnamed: 5': '麻薬', 'Unnamed: 6': '業者名追記'})
    filepath_new = files[0].parent / (files[0].stem[:-3] + '.csv')
    df.to_csv(filepath_new, index=False, encoding='utf8')

    # excel削除
    if delete_tmp:
        for filepath in files:
            filepath.unlink()

    return str(filepath_new)


def read_mhlw_price(*, year: Optional[int] = None, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """厚労省HPから、(1)-(4)薬価基準収載品目リストを取得する。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        save_dir: 指定した場合、取得したマスタを `save_dir`にcsv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    return _MedicineMaster.read(download_mhlw_price, year=year, save_dir=save_dir, numeric_cols=['薬価'])


#
# 厚労省 後発医薬品 (mhlw_ge)
#
def download_mhlw_ge(save_dir: Union[str, os.PathLike], *, year: Optional[int] = None, delete_tmp=True) -> str:
    """厚労省HPから、(5)後発医薬品に関する情報の一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        year: マスタの公開年度。指定しない場合は最新年度。
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.xlsx) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    url = get_url_mhlw(year=year)
    soup = _MedicineMaster.get(url)

    links = soup.select('#contents .ico-excel a')
    links = [link for link in links if link.attrs['href'].endswith('_05.xlsx')]  # ファイル名の形式でフィルター
    base_url = 'https://www.mhlw.go.jp'
    download_url = base_url + '/' + links[0].attrs['href']

    # ファイルの保存
    filepath = _MedicineMaster.fetch_file(download_url, save_dir)

    # ファイル形式の変換
    df = pd.read_excel(filepath, dtype=str)
    df = df.rename(columns={'収載年月日(YYYYMMDD)\n【例】\n2016年4月1日\n(20160401)': '収載年月日(YYYYMMDD)'})
    filepath_new = filepath.parent / (filepath.stem + '.csv')
    df.to_csv(filepath_new, index=False, encoding='utf8')

    # excel削除
    if delete_tmp:
        filepath.unlink()

    return str(filepath_new)


def read_mhlw_ge(*, year: Optional[int] = None, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """厚労省HPから、(5)後発医薬品に関する情報を取得する。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        save_dir: 指定した場合、取得したマスタを `save_dir`にcsv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    return _MedicineMaster.read(download_mhlw_ge, year=year, save_dir=save_dir, numeric_cols=[])
