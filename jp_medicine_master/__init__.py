from logging import getLogger
import os
from pathlib import Path
from typing import Union, Optional, List
import zipfile

from bs4 import BeautifulSoup
import pandas as pd
import requests

# ログ設定
logger = getLogger(__name__)

# ファイル保存元URL
url_ssk = "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r06/kihonmasta_04.html"
url_mhlw = "https://www.mhlw.go.jp/topics/2024/04/tp20240401-01.html"

# requests用パラメータ
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}
timeout_sec = 60


#
# 内部用
#
def _fetch_file(download_url: str, save_dir: Union[str, os.PathLike], *, delete_tmp=True) -> Path:
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


def _read(download_func, save_dir: Optional[Union[str, os.PathLike]], numeric_cols: List[str] = []):
    """対象ファイルをホームディレクトリにダウンロード -> pandas.DataFrameとして読み込み -> ダウンロードファイルを削除"""
    # 保存先フォルダ
    if save_dir is None:
        save_dir = Path.home() / '.jp_medicine_master'
        if not save_dir.is_dir():
            save_dir.mkdir()
        delete_csv = True

    # 対象ファイルのダウンロード
    filepath = download_func(save_dir, delete_tmp=True)

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
def download_ssk_y(save_dir: Union[str, os.PathLike], *, delete_tmp=True) -> str:
    """支払基金HPから、医薬品マスターの一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.zip) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    html = requests.get(url_ssk, timeout=timeout_sec, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')

    link = soup.select_one('.table01').find('a')
    base_url = '/'.join(url_ssk.split('/')[:-1])
    download_url = base_url + '/' + link.attrs['href']

    # ファイルの保存
    filepath = _fetch_file(download_url, save_dir, delete_tmp=delete_tmp)

    # ヘッダ行の追加
    filepath_header = Path(__file__).parent / 'ssk_y_header.csv'
    df1 = pd.read_csv(filepath_header, dtype=str, encoding='utf8')
    cols = df1.columns
    df2 = pd.read_csv(filepath, dtype=str, encoding='cp932', names=cols)
    df2.to_csv(filepath, index=False, encoding='utf8')

    return str(filepath)


def read_ssk_y(*, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """支払基金HPから、医薬品マスターを取得する。

    Args:
        save_dir: [Optional] 保存先フォルダ。指定した場合、csv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    return _read(download_ssk_y, save_dir, numeric_cols=['医薬品名・規格名漢字有効桁数', '医薬品名・規格名カナ有効桁数', '単位漢字有効桁数', '新又は現金額', '旧金額'])


#
# 厚労省 薬価 (mhlw_price)
#
def download_mhlw_price(save_dir: Union[str, os.PathLike], *, delete_tmp=True) -> str:
    """厚労省HPから、(1)-(4)薬価基準収載品目リストの一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.xlsx) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    html = requests.get(url_mhlw, timeout=timeout_sec, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')

    links = soup.select('#contents .ico-excel a')
    base_url = 'https://www.mhlw.go.jp'
    download_urls = [base_url + '/' + link.attrs['href'] for link in links[:4]]

    # ファイルの保存
    files = []
    for download_url in download_urls:
        filepath = _fetch_file(download_url, save_dir)
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


def read_mhlw_price(*, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """厚労省HPから、(1)-(4)薬価基準収載品目リストを取得する。

    Args:
        save_dir: [Optional] 保存先フォルダ。指定した場合、csv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    return _read(download_mhlw_price, save_dir, numeric_cols=['薬価'])


#
# 厚労省 後発医薬品 (mhlw_ge)
#
def download_mhlw_ge(save_dir: Union[str, os.PathLike], *, delete_tmp=True) -> str:
    """厚労省HPから、(5)後発医薬品に関する情報の一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.xlsx) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    html = requests.get(url_mhlw, timeout=timeout_sec, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')

    links = soup.select('#contents .ico-excel a')
    links = [link for link in links if link.attrs['href'].endswith('_05.xlsx')]  # ファイル名の形式でフィルター
    base_url = 'https://www.mhlw.go.jp'
    download_url = base_url + '/' + links[0].attrs['href']

    # ファイルの保存
    filepath = _fetch_file(download_url, save_dir)

    # ファイル形式の変換
    df = pd.read_excel(filepath, dtype=str)
    df = df.rename(columns={'収載年月日(YYYYMMDD)\n【例】\n2016年4月1日\n(20160401)': '収載年月日(YYYYMMDD)'})
    filepath_new = filepath.parent / (filepath.stem + '.csv')
    df.to_csv(filepath_new, index=False, encoding='utf8')

    # excel削除
    if delete_tmp:
        filepath.unlink()

    return str(filepath_new)


def read_mhlw_ge(*, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """厚労省HPから、(5)後発医薬品に関する情報を取得する。

    Args:
        save_dir: [Optional] 保存先フォルダ。指定した場合、csv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    return _read(download_mhlw_ge, save_dir, numeric_cols=[])

