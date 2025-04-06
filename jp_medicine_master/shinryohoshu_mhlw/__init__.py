from logging import getLogger
import os
from pathlib import Path
from typing import Union, Optional, Dict
import re
from urllib.parse import urljoin

import pandas as pd

from .._ import MasterDownloader

# ログ設定
logger = getLogger(__name__)


# ファイル保存元URL
def _get_download_url_shinryohoshu_mhlw(year: Optional[int] = None, *, verbose: bool = False) -> Union[str, Dict[int, str]]:
    """診療報酬情報提供サービスで公開されている医薬品マスタの、ダウンロードリンクurlを返す。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        verbose: Trueを指定した場合、リンクの一覧をdictとして返す。
    """
    download_urls = {
        2025: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/downloadMenu/yFile",
        2024: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/R06_y.zip",
        2023: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/R05_y.zip",
        2022: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/R04_y.zip",
        2021: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/R03_y.zip",
        2020: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/R02_y.zip",
        2019: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/R01_y.zip",  # 2019-10-01から適用
        2018: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/H30_y.zip",
        2016: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/H28_y.zip",
        2014: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/H26_y.zip",
        2012: "https://shinryohoshu.mhlw.go.jp/shinryohoshu/file/etc/H24_y.zip",
    }
    if verbose:
        return download_urls
    if year:
        if year not in download_urls:
            raise ValueError(f"{year} is not a valid value for year; supported values are {', '.join(download_urls.keys())}")
        if year == 2019:
            logger.warning('`year=2019` の医薬品マスタは、2019年10月の消費税率引上げによる改定後のマスタです。2019年9月までのマスタは `year=2018` を参照してください。')
        return download_urls[year]
    else:
        year = max(download_urls)
        return download_urls[year]


def _get_update_shinryohoshu_mhlw(year: int) -> str:
    """診療報酬情報提供サービスで公開されている医薬品マスタの、更新日yyyymmddを返す。

    Args:
        year: マスタの公開年度。
    """
    update_urls = {
        2023: '20240115',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaiteiR05"
        2022: '20230314',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaiteiR04"
        2021: '20220121',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaiteiR03"
        2020: '20210217',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaiteiR02"
        2019: '20200121',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaiteiR01"
        2018: '20190903',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaitei30"
        2016: '20180313',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaitei28"
        2014: '20160223',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaitei26"
        2012: '20140203',  # "https://shinryohoshu.mhlw.go.jp/shinryohoshu/kaitei/doKaitei24"
    }
    return update_urls.get(year, None)


#
# メイン関数 (y)
#
def download_y(save_dir: Union[str, os.PathLike], *, year: Optional[int] = None, file_info=False, delete_tmp=True) -> str:
    """診療報酬情報提供サービスから、医薬品マスターの一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        year: マスタの公開年度。指定しない場合は最新年度。
        file_info: Trueを指定した場合、DataFrameの末尾に`file`列を追加し、元ファイルの名前を表示する。
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.zip) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    download_url = _get_download_url_shinryohoshu_mhlw(year=year)

    # ファイルの保存
    update = _get_update_shinryohoshu_mhlw(year)
    if update:
        outfile_name = f'y_{update}.csv'
    else:
        outfile_name = None
    filepath = MasterDownloader.fetch_file(download_url, save_dir, delete_tmp=delete_tmp, outfile_name=outfile_name)

    # ヘッダ行の追加
    filepath_header = Path(__file__).parent / 'y_header.csv'
    df_header = pd.read_csv(filepath_header, dtype=str, encoding='utf8')
    cols = df_header.columns
    df = pd.read_csv(filepath, dtype=str, encoding='cp932', names=cols)

    # 元ファイルの情報
    if file_info:
        df['file'] = filepath.stem

    df.to_csv(filepath, index=False, encoding='utf8')

    return str(filepath)


def read_y(*, year: Optional[int] = None, save_dir: Optional[Union[str, os.PathLike]] = None, file_info=False) -> pd.DataFrame:
    """支払基金HPから、医薬品マスターを取得する。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        save_dir: 指定した場合、取得したマスタを `save_dir`にcsv形式 (UTF-8) で保存する。
        file_info: Trueを指定した場合、DataFrameの末尾に`file`列を追加し、元ファイルの名前を表示する。

    Return:
        `pd.DataFrame`
    """
    numeric_cols=['医薬品名・規格名漢字有効桁数', '医薬品名・規格名カナ有効桁数', '単位漢字有効桁数', '新又は現金額', '旧金額']
    return MasterDownloader.read(download_y, year=year, save_dir=save_dir, numeric_cols=numeric_cols, file_info=file_info)


def get_years_y():
    """`year` に指定できる年度の一覧。"""
    return list(sorted(_get_download_url_shinryohoshu_mhlw(verbose=True).keys()))
