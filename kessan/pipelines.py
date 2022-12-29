# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pdb
import pandas as pd
from itemadapter import ItemAdapter
# import pdb;pdb.set_trace()
import sqlite3

USE_PSQL = False

def get_brands():
    brands_sheet_url = f"https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    # ["日付", "コード", "銘柄名", "市場・商品区分", "33業種コード", "33業種区分", "17業種コード", "17業種区分", "規模コード", "規模区分"]
    return pd.read_excel(brands_sheet_url)


class KessanPipeline:

    def open_spider(self, spider):
        if USE_PSQL:
            hostname = 'postgres'
            username = 'takubo'
            password = "password" # your password
            database = 'stock_database'
            self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
            self.cur = self.connection.cursor()
        else:
            self.connection = sqlite3.connect('shows.db')
            self.cur = self.connection.cursor()
            
            # table作成
            try:
                query = '''
                    CREATE TABLE ticker_price (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT,
                        date TEXT,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume REAL,
                        n_transactions INTEGER,
                        transaction_amount REAL,
                        vwap REAL,
                        mcap TEXT
                        )
                    '''
                self.cur.execute(query)
            except Exception as e:
                if "already exists" not in str(e):
                    raise e
            
            res = self.cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='ticker_brand';")

            if len(res.fetchall()) == 0:
                
                # Create ticker_brand table if it doesn't exist
                query = """
                CREATE TABLE ticker_brand (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    name TEXT,
                    mcap TEXT
                )
                """
                self.cur.execute(query)
                # and insert data
                tickers = get_brands()["コード"].unique()
                # pdb.set_trace()
                values_string = "".join([f"({code}, {name}, '-1')," for code, name in tickers])
                query = "INSERT INTO ticker_brand (code, name, mcap) values" + values_string
                self.cur.execute(query)





    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        
        # TODO:
        # migrationは、djangoを通して実行する。
        # tableを作成し、データを格納したら、DB閲覧はdjangoを通して実施する。
        # 次はこちらのDB操作から。
        # self.cur.execute("SELECT * FROM ticker_price")
        
        query=f"""
            INSERT INTO ticker_price( close, code, date, high, low, n_transactions, open, transaction_amount, volume, vwap
                ) values({item['close']}, {item['code']}, '{item['date']}', {item['high']}, {item['low']}, {item['n_transactions']}, {item['open']}, {item['transaction_amount']}, {item['volume']}, {item['vwap']});"""
        # update brand field with mcap
        query_for_brand = f"""
            UPDATE ticker_brand SET mcap='{item['mcap']}' WHERE code = {item['code']}
        """
        
        self.cur.execute(query)
        self.cur.execute(query_for_brand)

        self.connection.commit()
        return item

