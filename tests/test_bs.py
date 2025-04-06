from pathlib import Path

import pytest
import jp_medicine_master as jpmed


def test_download_bs_all():
    save_dir = Path.home() / '.jp_medicine_master'
    if not save_dir.is_dir():
        save_dir.mkdir()

    years = jpmed.get_years_bs()
    for year in years:
        filepath = jpmed.download_bs(save_dir=save_dir, year=year)
        assert filepath


def test_read_bs():
    df = jpmed.read_bs()

    # ヘッダー行
    assert df.columns.to_list() == ['医薬品コード', '薬価基準収載医薬品コード', '基本漢字名称', 'BS区分', 'BS成分名']

    # 行数 ~ 200
    assert 100 <= len(df) <= 300

    # 区分
    assert set(df['BS区分'].unique()) == set(['先発', 'BS'])
