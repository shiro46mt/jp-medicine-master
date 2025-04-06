from logging import getLogger
import os
from pathlib import Path
import re
from typing import Union, Optional
import unicodedata

import pandas as pd

from ..  import read_y, read_ge, get_years_y, get_years_ge

# ログ設定
logger = getLogger(__name__)


def _get_bs_master(*, year: Optional[int] = None):
    """後発医薬品に関する情報を参照してBS一覧を作成し、最新の医薬品マスター（支払基金）と突合する。"""
    if year:
        available_years = get_years_bs()
        if year not in available_years:
            raise ValueError(f"{year} is not a valid value for year; supported values are {', '.join(available_years.keys())}")

    # 後発医薬品に関する情報
    ge = read_ge(year=year, file_info=True)
    update = re.findall(r'tp(\d{8})', ge['file'].to_list()[0])[0]

    # バイオ医薬品の抽出
    ge['BS成分名'] = (
        ge['成分名'].str.extract(r'［(.+)後続', expand=False)
        .fillna(ge['成分名'].str.extract(r'^(.+)（遺伝子組換え）', expand=False))
    )
    ge = ge[ge['BS成分名'].notna()]

    # バイオシミラー、バイオシミラーのある医薬品の抽出
    ge.loc[ge['各先発医薬品の後発医薬品の有無に関する情報'].isin(['3', '★']), 'BS区分'] = 'BS'
    ge.loc[ge['各先発医薬品の後発医薬品の有無に関する情報'].isin(['2', '☆']), 'BS区分'] = '先発'
    ge = ge[ge['BS区分'].notna()]

    # 医薬品マスター（支払基金）と突合
    y = read_y(year=year)
    master = (
        y[['医薬品コード', '薬価基準収載医薬品コード', '基本漢字名称']]
        .merge(
            ge[['薬価基準収載医薬品コード', 'BS区分', 'BS成分名']]
        )
    )

    return master, update


def _save_csv(df, save_dir: Union[str, os.PathLike], update: str) -> str:
    """`df` をcsv形式 (UTF-8) で保存する。"""
    # 保存先フォルダ
    if isinstance(save_dir, str):
        save_dir = Path(save_dir)

    if not isinstance(save_dir, Path) or not save_dir.is_dir():
        raise FileNotFoundError("No such directory: '%s'", save_dir)

    # ファイルの保存
    filepath = save_dir / f"BS_{update}.csv"
    df.to_csv(filepath, index=False, encoding='utf8')

    return str(filepath)


#
# メイン関数
#
def download_bs(save_dir: Union[str, os.PathLike], *, year: Optional[int] = None) -> str:
    """後発医薬品に関する情報からBSのリストを取得し、最新の医薬品マスター（支払基金）と突合したBS一覧を作成して、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ。
        year: マスタの公開年度。指定しない場合は最新年度。

    Return:
        保存先ファイルパス (str)
    """
    # BSのリスト
    df, update = _get_bs_master(year=year)

    # ファイルの保存
    return _save_csv(df, save_dir, update)


def read_bs(*, year: Optional[int] = None, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """後発医薬品に関する情報からBSのリストを取得し、最新の医薬品マスター（支払基金）と突合したBS一覧を作成する。

    Args:
        year: マスタの公開年度。指定しない場合は最新年度。
        save_dir: 指定した場合、取得したマスタを `save_dir`にcsv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    # BSのリスト
    df, update = _get_bs_master(year=year)

    # ファイルの保存
    if save_dir:
        _save_csv(df, save_dir, update)

    return df


def get_years_bs():
    """`year` に指定できる年度の一覧。"""
    years_y = get_years_y()
    years_ge = get_years_ge()
    return [year for year in years_y if year in years_ge]
