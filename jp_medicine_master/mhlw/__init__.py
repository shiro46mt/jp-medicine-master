from logging import getLogger
import os
from typing import Union, Optional, Dict

import pandas as pd

from .._ import MasterDownloader

# ログ設定
logger = getLogger(__name__)


# ファイル保存元URL
def _get_url_mhlw(year: Optional[int] = None, *, verbose: bool = False) -> Union[str, Dict[int, str]]:
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


#
# メイン関数 | 厚労省 薬価 (mhlw_price)
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
    url = _get_url_mhlw(year=year)
    soup = MasterDownloader.get(url)

    links = soup.select('#contents .ico-excel a')
    base_url = 'https://www.mhlw.go.jp'
    download_urls = [base_url + '/' + link.attrs['href'] for link in links[:4]]

    # ファイルの保存
    files = []
    for download_url in download_urls:
        filepath = MasterDownloader.fetch_file(download_url, save_dir)
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
    return MasterDownloader.read(download_mhlw_price, year=year, save_dir=save_dir, numeric_cols=['薬価'])


#
# メイン関数 | 厚労省 後発医薬品 (mhlw_ge)
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
    url = _get_url_mhlw(year=year)
    soup = MasterDownloader.get(url)

    links = soup.select('#contents .ico-excel a')
    links = [link for link in links if link.attrs['href'].endswith('_05.xlsx')]  # ファイル名の形式でフィルター
    base_url = 'https://www.mhlw.go.jp'
    download_url = base_url + '/' + links[0].attrs['href']

    # ファイルの保存
    filepath = MasterDownloader.fetch_file(download_url, save_dir)

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
    return MasterDownloader.read(download_mhlw_ge, year=year, save_dir=save_dir, numeric_cols=[])


#
# メイン関数 | 共通
#
def get_years_mhlw():
    """`year` に指定できる年度の一覧。"""
    return list(sorted(_get_url_mhlw(verbose=True).keys))
