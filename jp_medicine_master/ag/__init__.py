from logging import getLogger
import os
from pathlib import Path
import re
from typing import Union, Optional
import unicodedata

from bs4 import BeautifulSoup
import pandas as pd
import requests

from ..  import read_ssk_y

# ログ設定
logger = getLogger(__name__)


def _normalize(s):
    """表記揺らぎの矯正"""
    return unicodedata.normalize("NFKC", re.sub(r'\s', '', s)).replace('−', '-')


def _get():
    """日経メディカルのHPからAG一覧を取得"""
    # requests用パラメータ
    headers = {'User-Agent': ''}
    timeout_sec = 60

    # ダウンロード用リンクの取得
    url = 'https://medical.nikkeibp.co.jp/inc/all/drugdic/ag/index.html'
    html = requests.get(url, timeout=timeout_sec, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')

    # 更新日
    update = soup.select_one('#drugindex-header > p').get_text()
    mob = re.search(r'(\d+)年(\d+)月(\d+)日', update).groups()
    update = f'{int(mob[0]):0>4d}{int(mob[1]):0>2d}{int(mob[2]):0>2d}'

    # AG一覧
    items = []
    for item in soup.select_one('#article02').find_all('li'):
        divs = item.find_all('div')
        s_name = _normalize(divs[0].get_text())
        s_name, s_maker, *_ = re.split('[()]', s_name)
        ag_code = divs[1].find('a').attrs['href'].split('/')[-1][:12]
        ag_name = _normalize(divs[1].get_text())
        ag_maker = _normalize(divs[2].get_text())
        items.append([s_name, s_maker, ag_code, ag_name, ag_maker])

    return items, update


def _get_ag_master():
    """AG一覧を最新の医薬品マスター（支払基金）と突合する。"""
    # AGのリスト
    items, update = _get()

    # 医薬品マスタ（支払基金）
    master = read_ssk_y()[['医薬品コード', '薬価基準収載医薬品コード', '基本漢字名称']]
    master.index = master['基本漢字名称'].apply(_normalize)

    # AG区分
    master['AG区分'] = ''
    master['YJコード'] = master['薬価基準収載医薬品コード']
    for s_name, s_maker, ag_code, ag_name, ag_maker in items:
        if ag_code == '##':
            continue

        if s_name in master.index:
            master.loc[s_name, 'AG区分'] = '先発'
        elif s_name.endswith('mg') and s_name[:-2] in master.index:
            # 製品名にmgが含まれないパターン（ブロプレス、リーマス）
            s_name = s_name[:-2]
            master.loc[s_name, 'AG区分'] = '先発'
        elif 'OD' in s_name and s_name.endswith('錠') and s_name[:-1].replace('OD', 'OD錠'):
            # 「OD錠0mg」が「OD0mg錠」となったパターン（タリオン）
            s_name = s_name[:-1].replace('OD', 'OD錠')
            master.loc[s_name, 'AG区分'] = '先発'
        elif not re.search(r'\d', s_name):
            # 規格が省略されたパターン（アクトス錠、アレジオン点眼、ベルケイド注射用、メトグルコ錠）
            s_names = [s for s in master.index if s.startswith(s_name) and '(選)' not in s]
            master.loc[s_names, 'AG区分'] = '先発'
        else:
            logger.warning(f"先発品 '{s_name}' は医薬品マスターに見つかりませんでした。")

        if ag_name in master.index:
            master.loc[ag_name, 'AG区分'] = 'AG'
            master.loc[ag_name, 'YJコード'] = ag_code
        else:
            logger.warning(f"AG '{ag_name}' は医薬品マスターに見つかりませんでした。")

    return master[master['AG区分'] != ''].reset_index(drop=True), update


def _save_csv(df, save_dir: Union[str, os.PathLike], update: str) -> str:
    """`df` をcsv形式 (UTF-8) で保存する。"""
    # 保存先フォルダ
    if isinstance(save_dir, str):
        save_dir = Path(save_dir)

    if not isinstance(save_dir, Path) or not save_dir.is_dir():
        raise FileNotFoundError("No such directory: '%s'", save_dir)

    # ファイルの保存
    filepath = save_dir / f"AG一覧_{update}.csv"
    df.to_csv(filepath, index=False, encoding='utf8')

    return str(filepath)


#
# メイン関数
#
def download_ag(save_dir: Union[str, os.PathLike]) -> str:
    """日経メディカルのHPからAGのリストを取得し、最新の医薬品マスター（支払基金）と突合したAG一覧を作成して、csv形式 (UTF-8) で保存する。

    Args:
        save_dir: 保存先フォルダ。

    Return:
        保存先ファイルパス (str)
    """
    # AGのリスト
    df, update = _get_ag_master()

    # ファイルの保存
    return _save_csv(df, save_dir, update)


def read_ag(*, save_dir: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    """日経メディカルのHPからAGのリストを取得し、最新の医薬品マスター（支払基金）と突合したAG一覧を作成する。

    Args:
        save_dir: 指定した場合、取得したマスタを `save_dir`にcsv形式 (UTF-8) で保存する。

    Return:
        `pd.DataFrame`
    """
    # AGのリスト
    df, update = _get_ag_master()

    # ファイルの保存
    if save_dir:
        _save_csv(df, save_dir, update)

    return df
