import pytest
import jp_medicine_master as jpmed


def test_read_ag():
    df = jpmed.read_ag()

    # ヘッダー行
    assert df.columns.to_list() == ['医薬品コード', '薬価基準収載医薬品コード', '基本漢字名称', 'AG区分', 'YJコード']

    # 行数 ~ 400
    assert 200 <= len(df) <= 600

    # 区分
    assert set(df['AG区分'].unique()) == set(['先発', 'AG'])
