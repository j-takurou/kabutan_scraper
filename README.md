# 決算情報・株価データを収集するScraper system

## Data Source 
- kabutan

## How to Use 
1. github secretsにS3利用するためのaccess keysの情報を下記の変数名で追加する
    - ```
    ACCESS_KEY_ID=xxxxxxx
    SECRET_ACCESS_KEY=yyyyyyyy
    ```
2'. `scrapy crawl price`をdockercompose経由で実行
2. github actionでバッチ実行する
