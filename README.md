[![pytest](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml/badge.svg)](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml)
![GitHub License](https://img.shields.io/github/license/shiro46mt/jp-medicine-master)
[![PyPI - Version](https://img.shields.io/pypi/v/jp-medicine-master)](https://pypi.org/project/jp-medicine-master/)

# jp-medicine-master
日本で使用される医薬品マスタを簡単に取得・利用するためのライブラリ

## 利用可能な医薬品マスタ
- レセプト電算処理システム用医薬品マスタ (ssk_y)
- 薬価基準収載医薬品 (mhlw_price)
- 後発医薬品に関する情報 (mhlw_ge)

# インストール方法
```
pip install jp-medicine-master
```

# 使用方法
```
import jp_medicine_master as jpmed

# 保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_ssk_y(save_dir)
print(filepath)  # /path/to/directory/y_20240906.csv

# 読み込む場合
df = jpmed.read_ssk_y()
```

# License
This software is released under the MIT License, see LICENSE.
