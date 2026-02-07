from logging import getLogger
from typing import Optional, Union
import warnings

import pandas as pd
import requests


# ログ設定
logger = getLogger(__name__)

# initialize
data_catalog = None

def _pull_data_catalog():
    global data_catalog

    # JSONファイルのURL
    url = "https://raw.githubusercontent.com/shiro46mt/jp-medicine-master-data/main/data/data_catalog.json"

    try:
        # requests用パラメータ
        request_headers = {'User-Agent': ''}
        timeout_sec = 60

        # URLにGETリクエストを送信
        response = requests.get(url, timeout=timeout_sec, headers=request_headers)

        # HTTPステータスコードが200 OKか確認
        response.raise_for_status()

        # JSONレスポンスをPythonの辞書に変換
        data_catalog = response.json()
        logger.info("Data catalog: updated at '%s'", data_catalog['update'])

        return True

    except requests.exceptions.RequestException:
        return False


if not _pull_data_catalog():
    warnings.warn("データカタログが取得できませんでした。インターネットの接続状況を確認してください。")


def _select_file(kind: str, date: Union[int, str, None] = None, year: Union[int, str, None] = None, kaitei: Union[int, str, None] = None) -> str:
    # データカタログの更新を確認
    if data_catalog is None:
        if not _pull_data_catalog():
            raise RuntimeError("データカタログが取得できませんでした。インターネットの接続状況を確認して再試行してください。")

    # データカタログからファイルの一覧を取得
    data_catalog_items = [item for item in data_catalog['data'] if item['id'] == kind]
    assert len(data_catalog_items) > 0, f"引数 kind の値が無効です: '{kind}'"
    files = data_catalog_items[0]['files']

    # 日付でファイルを指定
    if date:
        date = str(date)
        year = int(date[:4])
        month = int(date[4:6])

        # date でフィルターした後、翌年度の薬価改定時のファイルを除外する
        files = [f for f in files if f[-12:-4] <= date]
        if month < 4 or date == '20190930':
            files = [f for f in files if not f.startswith(f'{year}/')]

        assert len(files) > 0, f"引数 date の値が無効です。有効なファイルが存在しません: '{date}'"

    # 会計年度でファイルを指定
    elif year:
        year = int(year)

        # 年度末の日付でフィルターし、翌年度の薬価改定時のファイルを除外する
        date = f'{year+1}0331'
        files = [f for f in files if f[-12:-4] <= date and not f.startswith(f'{year+1}/')]

        assert len(files) > 0, f"引数 year の値が無効です。有効なファイルが存在しません: '{year}'"

    # 薬価改定年でファイルを指定
    elif kaitei:
        files = [f for f in files if f.startswith(f'{kaitei}/')]

        assert len(files) > 0, f"引数 kaitei の値が無効です。有効なファイルが存在しません: '{kaitei}'"

    # ファイル名が辞書順最後のファイルを返す
    return max(files)


def _read(kind: str, date: Union[int, str, None] = None, year: Union[int, str, None] = None, kaitei: Union[int, str, None] = None, *, numeric_cols: Optional[list[str]] = None) -> pd.DataFrame:
    # ファイルを選択
    filename = _select_file(kind=kind, date=date, year=year, kaitei=kaitei)
    logger.info("Downloading 'data/%s/%s'", kind, filename)

    # データリポジトリからファイルを取得
    url = f'https://raw.githubusercontent.com/shiro46mt/jp-medicine-master-data/main/data/{kind}/{filename}'
    df = pd.read_csv(url, header=0, dtype=str)

    # 数値型の列を変換
    if numeric_cols:
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c].str.replace(',', ''))

    return df


def read_y(date: Union[int, str, None] = None, year: Union[int, str, None] = None, kaitei: Union[int, str, None] = None) -> pd.DataFrame:
    """レセプト電算処理システムの医薬品マスターを読み込む。

    引数が未指定の場合は利用可能な最新データを読み込む。

    Args:
        date (yyyymmdd形式): 指定した日付時点での最新データを読み込む。
        year: 指定した年度の最新データを読み込む。dateを指定した場合は無視される。
        kaitei: 指定した薬価改定年度の最新データを読み込む。薬価改定、中間年改定のない年度を指定するとエラーになる。date,yearを指定した場合は無視される。
    """
    numeric_cols=[
        '変更区分','医薬品名・規格名漢字有効桁数','医薬品名・規格名カナ有効桁数','単位コード','単位漢字有効桁数',
        '金額種別','新又は現金額','麻薬・毒薬・覚醒剤原料・向精神薬','神経破壊剤','生物学的製剤',
        '後発品','歯科特定薬剤','造影（補助）剤','注射容量','収載方式等識別',
        '旧金額金額種別','旧金額','漢字名称変更区分','カナ名称変更区分','剤形',
        '一般名処方加算対象区分','抗ＨＩＶ薬区分','選定療養区分']
    return _read('y', date=date, year=year, kaitei=kaitei, numeric_cols=numeric_cols)


def read_price(date: Union[int, str, None] = None, year: Union[int, str, None] = None, kaitei: Union[int, str, None] = None) -> pd.DataFrame:
    """薬価基準収載品目リスト（厚生労働省）を読み込む。

    引数が未指定の場合は利用可能な最新データを読み込む。

    Args:
        date (yyyymmdd形式): 指定した日付時点での最新データを読み込む。
        year: 指定した年度の最新データを読み込む。dateを指定した場合は無視される。
        kaitei: 指定した薬価改定年度の最新データを読み込む。薬価改定、中間年改定のない年度を指定するとエラーになる。date,yearを指定した場合は無視される。
    """
    numeric_cols = ['薬価']
    return _read('mhlw_price', date=date, year=year, kaitei=kaitei, numeric_cols=numeric_cols)


def read_ge(date: Union[int, str, None] = None, year: Union[int, str, None] = None, kaitei: Union[int, str, None] = None) -> pd.DataFrame:
    """後発医薬品に関する情報（厚生労働省）を読み込む。

    引数が未指定の場合は利用可能な最新データを読み込む。

    Args:
        date (yyyymmdd形式): 指定した日付時点での最新データを読み込む。
        year: 指定した年度の最新データを読み込む。dateを指定した場合は無視される。
        kaitei: 指定した薬価改定年度の最新データを読み込む。薬価改定、中間年改定のない年度を指定するとエラーになる。date,yearを指定した場合は無視される。
    """
    numeric_cols = []
    return _read('mhlw_ge', date=date, year=year, kaitei=kaitei, numeric_cols=numeric_cols)


def read_hot13(date: Union[int, str, None] = None, year: Union[int, str, None] = None) -> pd.DataFrame:
    """HOTコードマスター（HOT13）を読み込む。

    引数が未指定の場合は利用可能な最新データを読み込む。

    Args:
        date (yyyymmdd形式): 指定した日付時点での最新データを読み込む。
        year: 指定した年度の最新データを読み込む。dateを指定した場合は無視される。
    """
    numeric_cols = ['包装単位数','包装総量数','更新区分']
    return _read('hot13', date=date, year=year, numeric_cols=numeric_cols)


def read_hot9(date: Union[int, str, None] = None, year: Union[int, str, None] = None) -> pd.DataFrame:
    """HOTコードマスター（HOT9）を読み込む。

    引数が未指定の場合は利用可能な最新データを読み込む。

    Args:
        date (yyyymmdd形式): 指定した日付時点での最新データを読み込む。
        year: 指定した年度の最新データを読み込む。dateを指定した場合は無視される。
    """
    numeric_cols = ['包装単位数','包装総量数','更新区分']
    return _read('hot9', date=date, year=year, numeric_cols=numeric_cols)
