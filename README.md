[![pytest](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml/badge.svg)](https://github.com/shiro46mt/jp-medicine-master/actions/workflows/pytest.yml)
![GitHub License](https://img.shields.io/github/license/shiro46mt/jp-medicine-master)
[![PyPI - Version](https://img.shields.io/pypi/v/jp-medicine-master)](https://pypi.org/project/jp-medicine-master/)
[![PyPI Downloads](https://static.pepy.tech/badge/jp-medicine-master)](https://pepy.tech/projects/jp-medicine-master)

# jp-medicine-master
日本で使用される医薬品マスタを簡単に取得・利用するためのライブラリ

## 利用可能な医薬品マスタ
- **レセプト電算処理システム用医薬品マスター**

    対応年度: 2012, 2014, 2016, 2018, 2019, 2020, 2022, 2024 (version>=1.2)

    出典: 社会保険診療報酬支払基金「基本マスター」
    https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/index.html

    🎉令和6年7月12日掲載[「医薬品マスターのレイアウト変更について」](https://www.ssk.or.jp/seikyushiharai/tensuhyo/kihonmasta/r06kaiteijoho.files/r06kaitei_20240712.pdf)に対応。

- **薬価基準収載医薬品**
- **後発医薬品に関する情報**

    対応年度: 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024 (version>=1.3) 2025 (version>=1.4)

    出典: 厚生労働省「薬価基準収載品目リスト及び後発医薬品に関する情報について」
    https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000078916.html

- **AG（オーソライズド・ジェネリック）一覧**

    日経メディカルのHPからAGの一覧を取得し、レセ電システム用医薬品マスターと突合して各種コードを付与したマスタです。(version>=1.4)

    出典: 日経メディカル処方薬事典｜AG（オーソライズドジェネリック）一覧
    https://medical.nikkeibp.co.jp/inc/all/drugdic/ag/index.html

> [!TIP]
>
> 最新年度のマスタが取得できない場合、ライブラリのアップデートをお試しください。
> ```
> pip install --upgrade jp-medicine-master
> ```
> それでも取得できない場合はissueなどでお知らせいただけると非常に光栄です。

# インストール方法
```
pip install jp-medicine-master
```

# 使用方法
```
import jp_medicine_master as jpmed
```

各マスタについて、2種類の関数が実装されています。read_xxx系の関数でも、引数save_dirを渡せば DataFrameとして読み込みつつcsvとして保存することも可能です。

* csvとして保存する関数（download_xxx）
* pandasのDataFrameとして読み込む関数（read_xxx）

以下のマスタでは、引数`year`を指定することで過去のバージョンを取得できます。
- レセプト電算処理システム用医薬品マスター
- 薬価基準収載医薬品
- 後発医薬品に関する情報

> [!TIP]
>
> 2019年度の医薬品マスタは、2019年10月の消費税率引上げによる改定後のマスタです。
> 2019年9月までのマスタは `year=2018` を参照してください。


**レセプト電算処理システム用医薬品マスタ**

```
# csvとして保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_ssk_y(save_dir)
print(filepath)  # /path/to/directory/y_ALL20241205.csv

# pandasのDataFrameとして読み込む場合
df = jpmed.read_ssk_y()
```

**薬価基準収載医薬品**

```
# csvとして保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_mhlw_price(save_dir)
print(filepath)  # /path/to/directory/tp20241206-01.csv

# pandasのDataFrameとして読み込む場合
df = jpmed.read_mhlw_price()
```

**後発医薬品に関する情報**

```
# csvとして保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_mhlw_ge(save_dir)
print(filepath)  # /path/to/directory/tp20241206-01_05.csv

# pandasのDataFrameとして読み込む場合
df = jpmed.read_mhlw_ge()
```

**AG（オーソライズド・ジェネリック）一覧**

```
# csvとして保存する場合
save_dir = '/path/to/directory'
filepath = jpmed.download_ag(save_dir)
print(filepath)  # /path/to/directory/ag_20250203.csv

# pandasのDataFrameとして読み込む場合
df = jpmed.read_ag()
```

# License
This software is released under the MIT License, see LICENSE.
