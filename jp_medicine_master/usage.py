from typing import Union

import pandas as pd

from . import read_y, read_ge, read_hot9


def get_y_all(year: Union[int, str]):
    """レセプト電算処理システム 医薬品マスターを取得する。

    read_y() との違い:
        年度途中で経過措置期限切れとなった医薬品の情報を含む。
    """
    # 年度末時点の医薬品マスター
    y1 = read_y(year=year)

    # 年度内の9月末時点の医薬品マスターのうち、変更区分が9:削除のレコード
    if str(year) == '2019':
        date = '20191001'
    else:
        date = f'{year}0928'
    y2 = read_y(date=date).query("変更区分 == 9")
    assert len(y2) > 0

    # 縦に連結
    df = pd.concat([y1, y2], axis=0).sort_values('医薬品コード')

    return df


def get_y_with_yj(date: Union[int, str, None] = None, year: Union[int, str, None] = None, kaitei: Union[int, str, None] = None):
    """レセプト電算処理システム 医薬品マスターに、HOTコードマスターを突合してYJコードを付与する。"""
    # 医薬品マスター
    y = read_y(date=date, year=year, kaitei=kaitei)

    # HOTコードマスターと突合
    if kaitei and (date is None) and (year is None):
        kaitei = int(kaitei)
        if kaitei < 2018:
            date = f"{kaitei+2}0331"
        elif kaitei == 2018:
            date = "20190930"
        else:
            date = f"{kaitei+1}0331"
    hot9 = (
        read_hot9(date=date, year=year)
        .rename(columns={'レセプト電算処理システムコード（１）': '医薬品コード', '個別医薬品コード': 'YJコード'})
        [['医薬品コード', 'YJコード']]
    )
    df = (
        y
        .merge(hot9, how='left')
        .merge(hot9, how='left', left_on='長期収載品関連', right_on='医薬品コード', suffixes=['', '_選'])  # （選）の製品の対応
    )
    df['YJコード'] = df['YJコード'].fillna(df['YJコード_選'])
    df = df.drop(columns=['医薬品コード_選', 'YJコード_選'])

    return df


def get_biosimilar(date: Union[int, str, None] = None, year: Union[int, str, None] = None, kaitei: Union[int, str, None] = None):
    """レセプト電算処理システム 医薬品マスターに、バイオシミラーに関する情報（BS区分、BS成分名）を付与して該当医薬品のみを抽出する。

    BSに関する情報は、後発医薬品に関する情報から加工。
    """
    # 後発医薬品に関する情報
    ge = read_ge(date=date, year=year, kaitei=kaitei)

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

    # 医薬品マスターと突合
    y = read_y(date=date, year=year, kaitei=kaitei)
    df = (
        y[['医薬品コード', '薬価基準収載医薬品コード', '基本漢字名称']]
        .merge(
            ge[['薬価基準収載医薬品コード', 'BS区分', 'BS成分名']]
        )
    )

    return df
