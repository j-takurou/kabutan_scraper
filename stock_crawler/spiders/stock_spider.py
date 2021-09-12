import scrapy


class StocksSpider(scrapy.Spider):
    name = "stocks"
    state = {}
    def start_requests(self):
        self.state["current_page"] = 1
        urls = [
            'https://kabutan.jp/news/',
            # 'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        
        # [@href="/news/?b=*."]
        datetime_list = response.css("td.news_time > time::text").extract()
        news_list = response.xpath('//a[contains(@href, "news/?b=")]').extract()
        for date, news in zip(datetime_list, news_list):
            yield {
                'date': date,
                'text': news
                # 'author': quote.css('small.author::text').get(),
                # 'tags': quote.css('div.tags a.tag::text').getall(),
            }

        # next_page = response.css('li.next a::attr(href)').get()
        
        # TODO:
        # 週次のデータしか取ってこれないように修正
        try:
            
            next_page = response.urljoin(f"?page={self.state['current_page']}")
            self.state['current_page'] = self.state.get('current_page', 0) + 1
            if self.state['current_page'] < 10:
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                return 
        except Exception as e:
            import pdb; pdb.set_trace()
            raise e
        #td > news_time > td > a > text
