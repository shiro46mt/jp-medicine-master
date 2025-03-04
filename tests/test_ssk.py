import pytest
import jp_medicine_master as jpmed
from jp_medicine_master.ssk import _get_url_ssk


def test_get_url_ssk():
    # 最新年度 == 2024
    assert _get_url_ssk() == _get_url_ssk(2024)


def test_read_ssk_y():
    df = jpmed.read_ssk_y()

    # ヘッダー行
    assert len(df.columns) == 42
    assert df.columns[0] == '変更区分'

    # 行数 ~ 20,000
    assert 18_000 <= len(df) <= 22_000
