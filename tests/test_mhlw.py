import pytest
import jp_medicine_master as jpmed
from jp_medicine_master.mhlw import _get_url_mhlw
from jp_medicine_master._ import MasterDownloader


def test_get_url_mhlw():
    # 最新年度 == 2025
    assert _get_url_mhlw() == _get_url_mhlw(2025)


def test_get_url_mhlw_verbose():
    urls = _get_url_mhlw(verbose=True)

    for year, url in urls.items():
        soup = MasterDownloader.get(url)
        assert soup is not None


#
# 厚労省 薬価 (mhlw_price)
#
def test_read_mhlw_price():
    df = jpmed.read_mhlw_price()

    # ヘッダー行
    assert len(df.columns) == 15
    assert df.columns[0] == '区分'

    # 行数 ~ 13,000
    assert 11_000 <= len(df) <= 15_000

    # 区分
    assert set(df['区分'].unique()) == set(['内用薬', '注射薬', '外用薬', '歯科用薬剤'])


def test_read_mhlw_price_with_file_info():
    df = jpmed.read_mhlw_price(file_info=True)

    # ヘッダー行
    assert len(df.columns) == 16
    assert df.columns[-1] == 'file'

    # file
    assert df['file'].nunique() == 4


#
# 厚労省 後発医薬品 (mhlw_ge)
#
def test_read_mhlw_ge():
    df = jpmed.read_mhlw_ge()

    # ヘッダー行
    assert len(df.columns) == 9
    assert df.columns[0] == '薬価基準収載医薬品コード'

    # 行数 ~ 13,000
    assert 11_000 <= len(df) <= 15_000


def test_read_mhlw_ge_with_file_info():
    df = jpmed.read_mhlw_ge(file_info=True)

    # ヘッダー行
    assert len(df.columns) == 10
    assert df.columns[-1] == 'file'
