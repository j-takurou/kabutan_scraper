import pdb
import scrapy

from kessan.items import KessanItem, PriceItem
from collections import defaultdict
import time
import requests
from bs4 import BeautifulSoup
import numpy as np
# from typing import Boolean
import re
import datetime as dt
from kessan.logger import logger

def get_brands():
    # brands_sheet_url = f"https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    # ["日付", "コード", "銘柄名", "市場・商品区分", "33業種コード", "33業種区分", "17業種コード", "17業種区分", "規模コード", "規模区分"]
    # pd.read_excel(brands_sheet_url)
    with open("code_list.txt", "r") as f:
        codes = f.readlines()
    return codes

def clean_numbers(num_str: str, is_int = True):
    if "." in num_str:
        # When num_str is float
        is_int = False
    if isinstance(num_str, (int, float)):
        return num_str
    unit = 1
    if re.match(string=num_str, pattern="百万円"):
        unit = 1_000_000
    elif re.match(string=num_str, pattern="億円"):
        unit = 100_000_000
    found_number_camma = re.findall(string=num_str, pattern="[,.\d]+")
    if len(found_number_camma) == 0:
        return 0
    else:
        number_camma = found_number_camma[0]
    if is_int:
        num_value = int("".join(number_camma).replace(",", ""))
    else:
        num_value = float("".join(number_camma).replace(",", ""))
    return num_value * unit


class StockSpider(scrapy.Spider):
    name = "price"
    # https://docs.scrapy.org/en/latest/topics/settings.html#settings-per-spider
    # custom_setting for specific item_pipeline
    def start_requests(self):
        tickers = get_brands()["コード"].unique()
        tickers = np.r_[tickers, ["0000", "0950"]] # 225とドル円為替情報も抜き取る
        for page in range(1, 2):
            for ticker in tickers:
                url = f"https://kabutan.jp/stock/kabuka?code={ticker}&ashi=day&page={page}"
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        time.sleep(0.5)
        try:
            # 時価総額
            mcap = -1
            captalization = response.css('th:contains("時価総額") ~ td' )
            
            if captalization:
                mcap = captalization.xpath("string()").extract_first()
            # price_table = response.css("table.stock_kabuka_dwm tr")
            table_rows = response.xpath('//table[@class="stock_kabuka_dwm"]//tr')

            # /div[@id="main"]/div
            from scrapy.selector import Selector
            price_table = Selector(response=response).css("table.stock_kabuka_dwm tr")
            # headers = [th.text for th in price_table[0] if th.text != "\n"]
            params = response.url.split("?")[1]
            params_dict = dict([p.split("=") for p in params.split("&")])
            try:
                headers = table_rows[0].xpath("th").xpath("string()")
            except IndexError:
                logger.error(f"'table.stock_kabuka_dwm tr'が存在しない: ticker code {params_dict['code']}")
                raise IndexError

            for row in table_rows[1:]:
                date = row.xpath("th").xpath("string()").get()
                date = dt.datetime.strptime(date, "%y/%m/%d")
                date = date.strftime("%Y/%m/%d")
                td_elems = [clean_numbers(elem.get()) for elem in row.xpath("td/text()")]
                if len(td_elems) == 5:
                    open, high, low, close, volume = td_elems
                elif len(td_elems) == 6:
                    # '前日比', '前日比％'を "_"に
                    open, high, low, close, _, volume = td_elems
                elif len(td_elems) == 7:
                    # '前日比', '前日比％'を "_"に
                    open, high, low, close, _, _, volume = td_elems
                
                yield PriceItem(
                    code=params_dict["code"],
                    date=date,
                    open=open,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                    n_transactions=-1,
                    transaction_amount=-1,
                    vwap=-1,
                    mcap=mcap,
                    )
                    # TODO:
                    # -1にしているカラムは、データを現時点では集めていないだけ。今後修正する
        except Exception as e:
            logger.error(f"{e}")
            raise e
