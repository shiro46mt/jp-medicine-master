import pytest
import jp_medicine_master as jpmed


def test_read_ssk_y():
    df = jpmed.read_ssk_y()
    assert df.columns[0] == '変更区分'


def test_read_mhlw_price():
    df = jpmed.read_mhlw_price()
    assert df.columns[0] == '区分'


def test_read_mhlw_ge():
    df = jpmed.read_mhlw_ge()
    assert df.columns[0] == '薬価基準収載医薬品コード'
