import concurrent
import requests
import json
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def download_and_save_page(page_number, progress_df):
    url = f'https://www.fontshop.com/search_data.json?page={page_number}&size=200&fields=typeface_data,opentype_features'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        filename = os.path.join('data', f'data_page_{page_number}.json')
        save_data_to_json(data, filename)
        print(f"Page {page_number} saved.")
        progress_df.at[page_number - 1, 'Completed'] = True
        progress_df.to_csv('progress.csv', index=False)
    except requests.exceptions.HTTPError as err:
        print(f"Error downloading page {page_number}: {err}")
        progress_df.at[page_number - 1, 'Completed'] = False
        progress_df.to_csv('progress.csv', index=False)


def main():
    total_hit = 57438
    total_page = round(total_hit / 200)

    if not os.path.exists('data'):
        os.makedirs('data')

    progress_df = pd.DataFrame(columns=['Page', 'Completed'])
    if os.path.exists('progress.csv'):
        progress_df = pd.read_csv('progress.csv')
    else:
        progress_df['Page'] = range(1, total_page + 1)
        progress_df['Completed'] = False

    with ThreadPoolExecutor(max_workers=10) as executor:
        pages_to_download = progress_df[progress_df['Completed'] == False]['Page']
        future_to_page = {executor.submit(download_and_save_page, page, progress_df): page for page in
                          pages_to_download}

        for future in concurrent.futures.as_completed(future_to_page):
            page = future_to_page[future]
            # Process the future's result if needed

    print("All pages saved.")


if __name__ == "__main__":
    main()
