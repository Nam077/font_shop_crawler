import concurrent

from download import FontCrawlerService
from concurrent.futures import ThreadPoolExecutor
import os
import json
import pandas as pd


def download_and_update_font(json_file_path, csv_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    csv_data = pd.read_csv(csv_path)
    for font in json_data:
        url_string = font["url_string"]
        if csv_data.loc[csv_data["url_string"] == url_string, "status"].values[0] == "Ok":
            print("Next")
            continue
        else:
            crawler = FontCrawlerService(data=font)
            result = crawler.save_font_data()
            if result is None:
                csv_data.loc[csv_data["url_string"] == url_string, "status"] = "Error"
            else:
                # cập nhật thêm trường path cho font  trong file json
                font["path"] = result
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
                csv_data.loc[csv_data["url_string"] == url_string, "status"] = "Ok"
                csv_data.to_csv(csv_path, index=False)
                print(f"Font {url_string} downloaded.")


def process_json_file(folder_work, json_file):
    json_file_path = os.path.join(folder_work, json_file)
    csv_file_path = os.path.join(folder_work, f"{json_file.replace('result', 'status').split('.')[0]}.csv")
    return (json_file_path, csv_file_path)


def main():
    folder_work = 'result'
    list_json_files = os.listdir(folder_work)
    list_json_files = [file for file in list_json_files if file.endswith('.json')]

    tasks = [process_json_file(folder_work, json_file) for json_file in list_json_files]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_and_update_font, json_file_path, csv_file_path) for
                   json_file_path, csv_file_path in tasks]

        completed_futures, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
        # Xử lý kết quả nếu cần
        for future in completed_futures:
            result = future.result()
            # Xử lý kết quả nếu cần


if __name__ == "__main__":
    main()
