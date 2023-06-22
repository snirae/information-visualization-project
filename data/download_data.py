import urllib.request
import json
import csv
import pandas as pd


def download_data(url, file_name):
    urllib.request.urlretrieve(url, file_name)


def read_json_file(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def write_csv_file(file_name, data):
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data[0].keys())
        for row in data:
            writer.writerow(row.values())


def read_csv_file(file_name):
    df = pd.read_csv(file_name, index_col='_id')
    return df


url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e&limit=700000'
url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=effd41e8-ddce-4683-b74e-31edce94b11e&limit=100000'
url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=b53b64f8-57ed-4213-9191-a7401c0cf436&limit=10000'

file_name = 'cr_r_q_ft.json'
file_name = 'sum_cr_r_q.json'
file_name = 'fellonies.json'

download_data(url, file_name)

x = read_json_file(file_name)

csv_name = 'cr_r_q_ft.csv'
csv_name = 'sum_cr_r_q.csv'
csv_name = 'fellonies.csv'

write_csv_file(csv_name, x['result']['records'])

df = read_csv_file(csv_name)
print(df.head())
print(df.shape)

