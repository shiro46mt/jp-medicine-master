import pytest
import jp_medicine_master as jpmed


def test_get_y_all():
    df = jpmed.get_y_all(year=2016)


def test_get_y_with_yj():
    df = jpmed.get_y_with_yj()


def test_get_biosimilar():
    df = jpmed.get_biosimilar()
