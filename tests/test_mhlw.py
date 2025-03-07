import pytest
import jp_medicine_master as jpmed
from jp_medicine_master.mhlw import _get_url_mhlw


def test_get_url_mhlw():
    # 最新年度 == 2025
    assert _get_url_mhlw() == _get_url_mhlw(2025)


def test_read_mhlw_price():
    df = jpmed.read_mhlw_price()

    # ヘッダー行
    assert len(df.columns) == 15
    assert df.columns[0] == '区分'

    # 行数 ~ 13,000
    assert 11_000 <= len(df) <= 15_000

    # 区分
    assert set(df['区分'].unique()) == set(['内用薬', '注射薬', '外用薬', '歯科用薬剤'])


def test_read_mhlw_ge():
    df = jpmed.read_mhlw_ge()

    # ヘッダー行
    assert len(df.columns) == 9
    assert df.columns[0] == '薬価基準収載医薬品コード'

    # 行数 ~ 13,000
    assert 11_000 <= len(df) <= 15_000
