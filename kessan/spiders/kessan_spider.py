import pdb
import scrapy
import re
import html
import pandas as pd
import datetime as dt
from pathlib import Path

import time

# today_str = dt.date.today().strftime("%Y%m%d")
target_date_str = "20221114"
target_date = dt.datetime.strptime(target_date_str, "%Y%m%d")
start_date = target_date - dt.timedelta(days=30)

class KessanSpider(scrapy.Spider):
    name = "kessan"

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
                    yield scrapy.Request(url=article_url, callback=self.parse_article)
                else:
                    raise StopIteration
        # pdb.set_trace()
        current_page = response.xpath('//div[@class="pagination"]//li//strong//text()').extract_first()
        next_page = int(current_page) + 1
        base_news_url = response.url.split("?")[0]
        yield scrapy.Request(url=base_news_url + "?page=" + str(next_page), callback=self.parse)

    def parse_article(self, response):
        
        title = response.xpath('//div[@id="h3div"]//h3').extract_first()
        code = re.findall(pattern="\d{4}", string=title)[0]
        
        updated_table = response.xpath('//div[@id="finance_box"]//table').extract_first()
        
        output_dir = Path(__file__).parent.parent / "output" 
        pd.read_html(updated_table)[0].to_excel(output_dir / f"{target_date_str}_{code}.xlsx", index=False)
        time.sleep(1.5)
    

    def parse_stock_prices(self, response):
        # url = f"https://kabutan.jp/stock/kabuka?code={ticker}&ashi=day&page={page}"

        pass
        
        
