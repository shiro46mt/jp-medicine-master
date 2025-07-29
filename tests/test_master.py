import pytest
import jp_medicine_master as jpmed
from jp_medicine_master.master import _select_file


def test_select_file_y():
    # date
    filename = _select_file(kind='y', date='20161219')
    assert filename == '2016/20161208.csv'

    filename = _select_file(kind='y', date='20161220')
    assert filename == '2016/20161220.csv'

    # year
    filename = _select_file(kind='y', year='2016')
    assert filename == '2016/20170322.csv'

    # kaitei
    filename = _select_file(kind='y', kaitei='2016')
    assert filename == '2016/20180313.csv'

    with pytest.raises(AssertionError) as e:
        filename = _select_file(kind='y', kaitei='2017')
    assert str(e.value) == "引数 kaitei の値が無効です。有効なファイルが存在しません: '2017'"

    filename = _select_file(kind='y', kaitei='2018')
    assert filename == '2018/20190903.csv'


def test_select_file_hot():
    # date
    filename = _select_file(kind='hot13', date='20161230')
    assert filename == '20161130.csv'

    filename = _select_file(kind='hot13', date='20161231')
    assert filename == '20161231.csv'

    # year
    filename = _select_file(kind='hot13', year='2016')
    assert filename == '20170331.csv'


def test_read_y():
    df = jpmed.read_y()


def test_read_price():
    df = jpmed.read_price()


def test_read_ge():
    df = jpmed.read_ge()


def test_read_hot13():
    df = jpmed.read_hot13()


def test_read_hot9():
    df = jpmed.read_hot9()
