import sqlite3
import os
import boto3

import datetime as dt
_today = dt.date.today().strftime("%Y-%m-%d")

def store_listdata_to_s3(data:list, bucket_name):

    ACCESS_KEY_ID = os.environ["ACCESS_KEY_ID"]
    SECRET_ACCESS_KEY = os.environ["SECRET_ACCESS_KEY"]
    s3 = boto3.resource(
        's3',
        region_name='us-east-1',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY
    )

    content = "\n".join(data)
    s3.Object(bucket_name, 'price_data.txt').put(Body=content)


def rotate_data():
    """ 月初めになったら先月分データを一式s3に送信する """
    conn = sqlite3.connect('shows.db')
    _cursor = conn.cursor()
    query = "SELECT * FROM ticker_price"
    res = _cursor.execute(query)
    data = res.fetchall()
    store_listdata_to_s3(data, bucket_name=_today)

    # https://www.ikkitang1211.site/entry/github-actions-secrets


# sqlite3のファイルをマージする方法
# https://stackoverflow.com/questions/80801/how-can-i-merge-many-sqlite-databases

if __name__ == "__main__":
    rotate_data()