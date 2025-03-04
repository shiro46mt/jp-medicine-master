from logging import getLogger
import os
from pathlib import Path
from typing import Union, Optional, Dict

import pandas as pd

from .._ import MasterDownloader

# ログ設定
logger = getLogger(__name__)


# ファイル保存元URL
def _get_url_ssk(year: Optional[int] = None, *, verbose: bool = False) -> Union[str, Dict[int, str]]:
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


#
# メイン関数
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
    url = _get_url_ssk(year=year)
    soup = MasterDownloader.get(url)

    link = soup.select_one('.table01').find('a')
    base_url = '/'.join(url.split('/')[:-1])
    download_url = base_url + '/' + link.attrs['href']

    # ファイルの保存
    filepath = MasterDownloader.fetch_file(download_url, save_dir, delete_tmp=delete_tmp)

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
    return MasterDownloader.read(download_ssk_y, year=year, save_dir=save_dir, numeric_cols=['医薬品名・規格名漢字有効桁数', '医薬品名・規格名カナ有効桁数', '単位漢字有効桁数', '新又は現金額', '旧金額'])


def get_years_ssk():
    """`year` に指定できる年度の一覧。"""
    return list(sorted(_get_url_ssk(verbose=True).keys))
