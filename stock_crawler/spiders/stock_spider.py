import scrapy


class StocksSpider(scrapy.Spider):
    name = "stocks"

    def start_requests(self):
        urls = [
            'https://kabutan.jp/news/?page=1',
            'https://kabutan.jp/news/?page=2'
            # 'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            # import pdb; pdb.set_trace()
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        
        page = response.url.split("/")[-2]
        filename = f'stock-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
