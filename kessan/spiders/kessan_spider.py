import pdb
import scrapy
import re
import html
import pandas as pd
import datetime as dt
from pathlib import Path
from kessan.items import KessanItem, PriceItem
import time

today_dt = dt.datetime.today()
# target_date_str = "20221114"
target_date_str = today_dt.strftime("%Y%m%d")
start_date = today_dt - dt.timedelta(days=30)

class KessanSpider(scrapy.Spider):
    name = "kessan"
    custom_settings = {
        'ITEM_PIPELINES': {'kessan.pipelines.KessanPipeline': 300},
    }
    def start_requests(self):
        urls = [
            'https://kabutan.jp/news/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        
        base_url = 'https://kabutan.jp'
        # request送信時、15件表示の結果HTMLが返ってくる。
        hrefs = [href for href in response.xpath('//div[@id="news_contents"]/table/@href')]
        for table in response.xpath('//div[@id="news_contents"]//table'):
            [a.xpath("@href").extract_first() for a in table.xpath('tr//a')]
            
            for tr in table.xpath('tr'):
                article_date = tr.xpath("td//time//@datetime").extract_first()
                article_date = dt.datetime.strptime(article_date, "%Y-%m-%dT%H:%M:%S+09:00")
                
                href = tr.xpath("td//a//@href").extract_first()
                article_url = base_url + href
                if article_date >= start_date:
                    yield scrapy.Request(
                        url=article_url, 
                        callback=self.parse_article,
                        cb_kwargs={"article_date": article_date}
                        )
                else:
                    raise StopIteration
        current_page = response.xpath('//div[@class="pagination"]//li//strong//text()').extract_first()
        next_page = int(current_page) + 1
        base_news_url = response.url.split("?")[0]
        time.sleep(1.5)
        yield scrapy.Request(url=base_news_url + "?page=" + str(next_page), callback=self.parse)

    def parse_article(self, response, article_date):
        
        title = response.xpath('//div[@id="h3div"]//h3').extract_first()
        code = re.findall(pattern="\d{4}", string=title)[0]
        
        updated_table = response.xpath('//div[@id="finance_box"]//table').extract_first()
        article_type = response.xpath('//div[@id="finance_box"]//h2')[0].get()
        article_type_h3 = response.xpath('//div[@id="finance_box"]//h3')[0].get()

        def get_fundamental(series):
            out = {}
            rename_necessary_cols = {
                "決算期":"period", 
                 "売上高":"sale",
                "営業益": "op_profit", 
                "経常益": "keijo_profit", 
                "最終益":"final_profit", 
                "１株配": "dividend", 
                "発表日": "release_date"
            }

            for col_name, item_name in rename_necessary_cols.items():
                out[item_name] = series.get(col_name) or "NULL"
            return out
        # pdb.set_trace()
        df = pd.read_html(updated_table)[0]
        row = df.iloc[-2, :]
        if "業績予想の修正" in article_type:
            # "決算期      売上高     営業益     経常益     最終益  修正1株益   １株配       発表日"
            columns = ["決算期", "売上高", "営業益", "経常益", "最終益", "修正1株益", "１株配", "発表日"]
            
            row = df.iloc[-2, :]
            data = get_fundamental(row)
        elif "今期の業績予想" in article_type:
            # pd.read_html(updated_table)
            data = get_fundamental(row)
            pass
        elif "配当予想の修正" in article_type:
            # 決算期  １株配       発表日
            columns = ["決算期", "１株配", "発表日"]
            data = get_fundamental(row)
            pass
        elif "前期【実績】" in article_type_h3:
            columns = ["決算期", "売上高", "営業益", "経常益", "最終益", "修正1株益", "１株配", "発表日"]
            data = get_fundamental(row)
        else:
            # pdb.set_trace()
            data = get_fundamental(row)
        return KessanItem(
            code=code,
            article_type=article_type,
            **data
        )
    

    def parse_stock_prices(self, response):
        # url = f"https://kabutan.jp/stock/kabuka?code={ticker}&ashi=day&page={page}"

        pass
        
        
