import os
import json
import concurrent.futures
import pandas as pd


def process_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        hits = data["families"]["hits"]["hits"]

        results = []
        for hit in hits:
            typeface_data = hit["_source"]["typeface_data"]
            name = hit["_source"]["name"]
            images = hit["_source"]["images"]
            designers = hit["_source"]["designers"]
            clean_name = hit["_source"]["clean_name"]
            id_font = hit["_id"]
            url_string = hit["_source"]["url_string"]
            result = {
                "typeface_data": typeface_data,
                "name": name,
                "images": images,
                "designers": designers,
                "clean_name": clean_name,
                "id": id_font,
                "url_string": url_string
            }
            results.append(result)

        result_file_path = os.path.join('result', f'{os.path.basename(file_path.split(".")[0])}_result.json')
        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            json.dump(results, result_file, ensure_ascii=False, indent=4)

        # Create DataFrame for CSV
        csv_data = [{"url_string": result["url_string"], "status": "False"} for result in results if
                    result["url_string"] is not None]
        csv_df = pd.DataFrame(csv_data)
        csv_file_path = os.path.join('result', f'{os.path.basename(file_path.split(".")[0])}_status.csv')
        csv_df.to_csv(csv_file_path, index=False)
        print(f"File {file_path} processed.")


def main():
    folder_path = 'data'
    list_json_files = os.listdir(folder_path)
    list_json_files = [file for file in list_json_files if file.endswith('.json')]

    os.makedirs('result', exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_json_file, [os.path.join(folder_path, file) for file in list_json_files])


if __name__ == "__main__":
    main()
