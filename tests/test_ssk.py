import pytest
import jp_medicine_master as jpmed
from jp_medicine_master.ssk import _get_url_ssk
from jp_medicine_master._ import MasterDownloader


def test_get_url_ssk():
    # 最新年度 == 2024
    assert _get_url_ssk() == _get_url_ssk(2024)


def test_get_url_ssk_verbose():
    urls = _get_url_ssk(verbose=True)

    for year, url in urls.items():
        soup = MasterDownloader.get(url)
        assert soup is not None


#
# 医薬品マスター
#
def test_read_ssk_y():
    df = jpmed.read_ssk_y()

    # ヘッダー行
    assert len(df.columns) == 42
    assert df.columns[0] == '変更区分'

    # 行数 ~ 20,000
    assert 18_000 <= len(df) <= 22_000


def test_read_ssk_y_with_file_info():
    df = jpmed.read_ssk_y(file_info=True)

    # ヘッダー行
    assert len(df.columns) == 43
    assert df.columns[-1] == 'file'
