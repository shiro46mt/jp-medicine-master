[![pytest](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml/badge.svg)](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml)
![GitHub License](https://img.shields.io/github/license/shiro46mt/jp-medicine-master)
[![PyPI - Version](https://img.shields.io/pypi/v/jp-medicine-master)](https://pypi.org/project/jp-medicine-master/)
[![PyPI Downloads](https://static.pepy.tech/badge/jp-medicine-master)](https://pepy.tech/projects/jp-medicine-master)

# jp-medicine-master
日本で使用される医薬品マスタを簡単に取得・利用するためのライブラリ

## 利用可能な医薬品マスタ
- **レセプト電算処理システム用医薬品マスタ**

    出典: 社会保険診療報酬支払基金「基本マスター」
    https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/index.html

    🎉令和6年7月12日掲載[「医薬品マスターのレイアウト変更について」](https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r06kaiteijoho.files/r06kaitei_20240712.pdf)に対応。

- **薬価基準収載医薬品**
- **後発医薬品に関する情報**

    出典: 厚生労働省「薬価基準収載品目リスト及び後発医薬品に関する情報について」
    https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000078916.html

# インストール方法
```
pip install jp-medicine-master
```

# 使用方法
```
import jp_medicine_master as jpmed
```

各マスタについて、csvとして保存する関数（download_xxx）と pandasのDataFrameとして読み込む関数（read_xxx）がある。


**レセプト電算処理システム用医薬品マスタ**
```
# csvとして保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_ssk_y(save_dir)  # /path/to/directory/y_ALL20241205.csv

# pandasのDataFrameとして読み込む場合
df = jpmed.read_ssk_y()
```

**薬価基準収載医薬品**
```
# csvとして保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_mhlw_price(save_dir)  # /path/to/directory/tp20241206-01.csv

# pandasのDataFrameとして読み込む場合
df = jpmed.read_mhlw_price()
```

**後発医薬品に関する情報**
```
# csvとして保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_mhlw_ge(save_dir)  # /path/to/directory/tp20241206-01_05.csv

# pandasのDataFrameとして読み込む場合
df = jpmed.read_mhlw_ge()
```

# License
This software is released under the MIT License, see LICENSE.
