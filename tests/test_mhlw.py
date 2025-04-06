from pathlib import Path

import pytest
import jp_medicine_master as jpmed


#
# 厚労省 薬価 (price)
#
def test_download_price_all():
    save_dir = Path.home() / '.jp_medicine_master'
    if not save_dir.is_dir():
        save_dir.mkdir()

    years = jpmed.get_years_price()
    for year in years:
        filepath = jpmed.download_price(save_dir=save_dir, year=year)
        assert filepath


def test_read_price():
    df = jpmed.read_price()

    # ヘッダー行
    assert len(df.columns) == 15
    assert df.columns[0] == '区分'

    # 行数 ~ 13,000
    assert 11_000 <= len(df) <= 15_000

    # 区分
    assert set(df['区分'].unique()) == set(['内用薬', '注射薬', '外用薬', '歯科用薬剤'])


def test_read_price_with_file_info():
    df = jpmed.read_price(file_info=True)

    # ヘッダー行
    assert len(df.columns) == 16
    assert df.columns[-1] == 'file'

    # file
    assert df['file'].nunique() == 4


@pytest.mark.filterwarnings("ignore:Use `.*_price` instead")
def test_price_alias():
    save_dir = Path.home() / '.jp_medicine_master'
    if not save_dir.is_dir():
        save_dir.mkdir()

    # read
    df = jpmed.read_mhlw_price()
    assert df is not None

    # download
    filepath = jpmed.download_mhlw_price(save_dir=save_dir)
    assert filepath


#
# 厚労省 後発医薬品 (ge)
#
def test_download_ge_all():
    save_dir = Path.home() / '.jp_medicine_master'
    if not save_dir.is_dir():
        save_dir.mkdir()

    years = jpmed.get_years_ge()
    for year in years:
        filepath = jpmed.download_ge(save_dir=save_dir, year=year)
        assert filepath


def test_read_ge():
    df = jpmed.read_ge()

    # ヘッダー行
    assert len(df.columns) == 9
    assert df.columns[0] == '薬価基準収載医薬品コード'

    # 行数 ~ 13,000
    assert 11_000 <= len(df) <= 15_000


def test_read_ge_with_file_info():
    df = jpmed.read_ge(file_info=True)

    # ヘッダー行
    assert len(df.columns) == 10
    assert df.columns[-1] == 'file'


@pytest.mark.filterwarnings("ignore:Use `.*_ge` instead")
def test_ge_alias():
    save_dir = Path.home() / '.jp_medicine_master'
    if not save_dir.is_dir():
        save_dir.mkdir()

    # read
    df = jpmed.read_mhlw_ge()
    assert df is not None

    # download
    filepath = jpmed.download_mhlw_ge(save_dir=save_dir)
    assert filepath
