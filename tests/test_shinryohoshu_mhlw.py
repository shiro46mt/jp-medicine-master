from pathlib import Path

import pytest
import jp_medicine_master as jpmed


#
# 医薬品マスター (y)
#
def test_download_y_all():
    save_dir = Path.home() / '.jp_medicine_master'
    if not save_dir.is_dir():
        save_dir.mkdir()

    years = jpmed.get_years_y()
    for year in years:
        filepath = jpmed.download_y(save_dir=save_dir, year=year)
        assert filepath


def test_read_y():
    df = jpmed.read_y()

    # ヘッダー行
    assert len(df.columns) == 42
    assert df.columns[0] == '変更区分'

    # 行数 ~ 20,000
    assert 18_000 <= len(df) <= 22_000


def test_read_y_with_file_info():
    df = jpmed.read_y(file_info=True)

    # ヘッダー行
    assert len(df.columns) == 43
    assert df.columns[-1] == 'file'
