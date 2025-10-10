import pytest
import jp_medicine_master as jpmed


def test_get_y_all():
    _ = jpmed.get_y_all(year=2016)
    _ = jpmed.get_y_all(year=2019)


def test_get_y_with_yj():
    _ = jpmed.get_y_with_yj()
    _ = jpmed.get_y_with_yj(year=2016)
    _ = jpmed.get_y_with_yj(kaitei=2019)


def test_get_biosimilar():
    _ = jpmed.get_biosimilar()
    _ = jpmed.get_biosimilar(year=2016)
