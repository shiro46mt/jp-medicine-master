[![pytest](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml/badge.svg)](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml)
![GitHub License](https://img.shields.io/github/license/shiro46mt/jp-medicine-master)
[![PyPI - Version](https://img.shields.io/pypi/v/jp-medicine-master)](https://pypi.org/project/jp-medicine-master/)
[![PyPI Downloads](https://static.pepy.tech/badge/jp-medicine-master)](https://pepy.tech/projects/jp-medicine-master)

# jp-medicine-master
日本で使用される医薬品マスターを簡単に取得・利用するためのライブラリ

## 利用可能な医薬品マスター
- **レセプト電算処理システム 医薬品マスター** : 2012年度薬価改定～

- **薬価基準収載医薬品** : 2014年度薬価改定～
- **後発医薬品に関する情報** : 2014年度薬価改定～
- **処方箋に記載する一般名処方の標準的な記載（一般名処方マスタ）** : 2016年度薬価改定～

- **HOTコードマスター（HOT13 / HOT9）** : 2001年～

# インストール方法
```
pip install jp-medicine-master
```

# 使用方法
```python
import jp_medicine_master as jpmed
```

## マスター読み込み
医薬品マスターをpandasのDataFrameとして読み込みます。引数の仕様は共通です。

```python
# レセプト電算処理システム 医薬品マスター
### 引数`date`を指定した場合は、指定日の時点のマスターを取得します。
df = jpmed.read_y(date='20161231')

# 薬価基準収載医薬品
### 引数`year`を指定した場合は、指定年度の末日の時点のマスターを取得します。
df = jpmed.read_price(year='2016')  # 2017年3月31日時点。

# 後発医薬品に関する情報
### 引数`kaitei`を指定した場合は、指定年度の薬価改定の有効期間の末日の時点のマスターを取得します。※HOTコードマスターは非対応。
df = jpmed.read_ge(kaitei='2016')  # 2018年3月31日時点。
df = jpmed.read_ge(kaitei='2018')  # 2019年9月30日時点。※2019年10月に消費税増税に伴う薬価改定があったため。

# 処方箋に記載する一般名処方の標準的な記載（一般名処方マスタ）
### 引数を指定しない場合は、現時点での最新マスターを取得します。
df = jpmed.read_ippanmeishohou()

# HOTコードマスター（HOT13 / HOT9）
df = jpmed.read_hot13()
df = jpmed.read_hot9()
```

## マスターの応用例
1つ以上の医薬品マスターを加工する使用例を実装しています。引数の仕様はマスター読み込みと同様です。

```python
# レセプト電算処理システム 医薬品マスターを取得します。
# read_y() との違いとして、年度途中で経過措置期限切れとなった医薬品の情報を含みます。※引数はyearのみ対応。
df = jpmed.get_y_all(year='2016')

# レセプト電算処理システム 医薬品マスターに、HOTコードマスターを突合してYJコードを付与します。
df = jpmed.get_y_with_yj()

# レセプト電算処理システム 医薬品マスターに、バイオシミラーに関する情報（BS区分、BS成分名）を付与して該当医薬品のみを抽出します。
# BSに関する情報は後発医薬品に関する情報から加工しています。
df = jpmed.get_biosimilar()
```

# データソース
[jp-medicine-master-data](https://github.com/shiro46mt/jp-medicine-master-data)を参照。

# License
This software is released under the MIT License, see LICENSE.
