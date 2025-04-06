from logging import getLogger
import os
from pathlib import Path
from typing import Union, Optional, Dict
from urllib.parse import urljoin

import pandas as pd
from typing_extensions import deprecated

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
        2025: "https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r06/kihonmasta_04.html",
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
# メイン関数 (ssk_y)
#
@deprecated('Use `download_y` instead')
def download_ssk_y(save_dir: Union[str, os.PathLike], *, year: Optional[int] = None, file_info=False, delete_tmp=True) -> str:
    """支払基金HPから、医薬品マスターの一覧ファイルをダウンロードし、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ
        year: マスタの公開年度。指定しない場合は最新年度。
        file_info: Trueを指定した場合、DataFrameの末尾に`file`列を追加し、元ファイルの名前を表示する。
        delete_tmp: Falseを指定した場合、ダウンロードした一時ファイル (.zip) を残す。

    Return:
        保存先ファイルパス (str)
    """
    # ダウンロード用リンクの取得
    url = _get_url_ssk(year=year)
    soup = MasterDownloader.get(url)

    # 原則、ページ内の最初の table.table01 にあるURLを取得する。
    # 中間年改訂があった場合、ページ内に複数年度が存在する場合があるので、年度を含むh2タグの直後の table.table01 にあるURLを取得する。
    h2_texts = {
        2024: '令和6年度',
    }
    if year in h2_texts:
        h2 = soup.find('h2', string=h2_texts[year])
        link = h2.find_next('table', class_='table01').find('a')
        download_url = urljoin(url, link.attrs['href'])
    else:
        link = soup.select_one('.table01').find('a')
        download_url = urljoin(url, link.attrs['href'])

    # ファイルの保存
    filepath = MasterDownloader.fetch_file(download_url, save_dir, delete_tmp=delete_tmp)

    # ヘッダ行の追加
    filepath_header = Path(__file__).parent / 'ssk_y_header.csv'
    df_header = pd.read_csv(filepath_header, dtype=str, encoding='utf8')
    cols = df_header.columns
    df = pd.read_csv(filepath, dtype=str, encoding='cp932', names=cols)

    # 元ファイルの情報
    if file_info:
        df['file'] = filepath.stem

    df.to_csv(filepath, index=False, encoding='utf8')

    return str(filepath)


@deprecated('Use `read_y` instead')
def read_ssk_y(*, year: Optional[int] = None, save_dir: Optional[Union[str, os.PathLike]] = None, file_info=False) -> pd.DataFrame:
    """支払基金HPから、医薬品マスターを取得する。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        save_dir: 指定した場合、取得したマスタを `save_dir`にcsv形式 (UTF-8) で保存する。
        file_info: Trueを指定した場合、DataFrameの末尾に`file`列を追加し、元ファイルの名前を表示する。

    Return:
        `pd.DataFrame`
    """
    numeric_cols=['医薬品名・規格名漢字有効桁数', '医薬品名・規格名カナ有効桁数', '単位漢字有効桁数', '新又は現金額', '旧金額']
    return MasterDownloader.read(download_ssk_y, year=year, save_dir=save_dir, numeric_cols=numeric_cols, file_info=file_info)


@deprecated('Use `get_years_y` instead')
def get_years_ssk_y():
    """`year` に指定できる年度の一覧。"""
    return list(sorted(_get_url_ssk(verbose=True).keys()))
