from logging import getLogger
import os
from pathlib import Path
from typing import Union, Optional, List
import zipfile

from bs4 import BeautifulSoup
import pandas as pd
import requests

# ログ設定
logger = getLogger(__name__)

# requests用パラメータ
headers = {'User-Agent': ''}
timeout_sec = 60


class MasterDownloader:
    @classmethod
    def get(self, url: str) -> BeautifulSoup:
        """urlへのHTTPアクセス"""
        html = requests.get(url, timeout=timeout_sec, headers=headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup

    @classmethod
    def fetch_file(self, download_url: str, save_dir: Union[str, os.PathLike], *, delete_tmp=True) -> Path:
        """download_urlのファイルをダウンロード -> zipの場合は解凍 -> ファイルを保存 -> ファイルパスを返す"""
        # 保存先フォルダ
        if isinstance(save_dir, str):
            save_dir = Path(save_dir)

        if not isinstance(save_dir, Path) or not save_dir.is_dir():
            raise FileNotFoundError("No such directory: '%s'", save_dir)

        # ダウンロードファイルの名前
        filename = download_url.split('/')[-1]
        filepath = save_dir / filename

        # ファイルダウンロード
        r = requests.get(download_url, stream=True)
        logger.info(f"Downloading from '{download_url}'")
        with open(filepath, 'wb') as zf:
            zf.write(r.content)

        # 拡張子が.zipでない場合は終了
        if filepath.suffix != '.zip':
            return filepath

        # zip解凍
        files = []
        with zipfile.ZipFile(filepath, 'r') as zf:
            for info in zf.infolist():
                info.filename = info.orig_filename.encode('cp437').decode('cp932')
                if os.sep != "/" and os.sep in info.filename:
                    info.filename = info.filename.replace(os.sep, "/")
                tmp = zf.extract(info, save_dir)
                files.append(Path(tmp))
        # zip削除
        if delete_tmp:
            filepath.unlink()

        return files[0]

    @classmethod
    def read(self, download_func, year: Optional[int] = None, save_dir: Union[str, os.PathLike, None] = None, numeric_cols: List[str] = []):
        """対象ファイルをホームディレクトリにダウンロード -> pandas.DataFrameとして読み込み -> ダウンロードファイルを削除"""
        # 保存先フォルダ
        if save_dir is None:
            save_dir = Path.home() / '.jp_medicine_master'
            if not save_dir.is_dir():
                save_dir.mkdir()
            delete_csv = True

        # 対象ファイルのダウンロード
        filepath = download_func(save_dir, year=year, delete_tmp=True)

        # 読み込み
        df = pd.read_csv(filepath, dtype=str, encoding='utf8')
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        # ダウンロードファイルの削除
        if delete_csv:
            Path(filepath).unlink()

        return df
