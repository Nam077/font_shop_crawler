from typing import List, Dict

import requests
import json
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

import os
import shutil
from concurrent.futures.thread import ThreadPoolExecutor
import pyzipper
import requests
import re
import json


class FontCrawlerService:
    def __init__(self, parent_folder='downloads', data=None):
        self.parent_folder = parent_folder
        self.url_string = data["url_string"]
        self.typeface_data = data["typeface_data"]
        self.folder_save = None
        self.result_urls = []

    def get_font_urls(self):
        font_urls = []
        for font in self.typeface_data:
            name = font["name"]
            url = font["webfont"]["url"]
            font_urls.append({"url": url, "name": name})
        self.result_urls = font_urls

    def create_save_folder(self):
        self.folder_save = os.path.join(self.parent_folder, self.url_string)
        if not os.path.exists(self.folder_save):
            os.makedirs(self.folder_save)

    def save_font_data(self) -> str or None:
        self.create_save_folder()
        prefix = "https://www.fontshop.com"
        self.get_font_urls()
        if len(self.result_urls) == 0:
            return None
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.fontshop.com/'
        }

        def download_font(font: Dict[str, str] = {"url": "", "name": ""}):
            def download_font_with_retry(font_download, base_url_download, save_path_download):
                max_retries = 5
                retries = 0
                while retries < max_retries:
                    try:
                        font_file = requests.get(base_url_download, stream=True)
                        font_file.raise_for_status()
                        with open(save_path_download, 'wb') as f:
                            f.write(font_file.content)
                        return True
                    except requests.exceptions.RequestException as e:
                        retries += 1
                        print(f"Error download font {font_download['name']} (Attempt {retries}/{max_retries}): {e}")
                return False

            url_request = prefix + font["url"]
            try:
                response = requests.get(url_request, headers=headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                return
            html = response.text
            url_match = re.search(r"url\('([^']*fast\.fonts\.net[^']*)'\)", html)
            if url_match:
                url = url_match.group(1)
                base_url = "https:" + url.split("?")[0]
                save_path = os.path.join(self.folder_save, f"{font['name']}.woff")
                if download_font_with_retry(font, base_url, save_path):
                    return save_path
            else:
                return

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_font, font) for font in self.result_urls]
            for future in futures:
                future.result()

        return self.create_zip_from_folder()

    def create_zip_from_folder(self):
        zip_filename = f"{self.url_string}.zip"
        zip_path = os.path.join(self.parent_folder, zip_filename)
        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(b"nvnfont")
            for root, dirs, files in os.walk(self.folder_save):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.folder_save)
                    zf.write(file_path, rel_path)

        if os.path.exists(self.folder_save):
            shutil.rmtree(self.folder_save)
        return zip_path
