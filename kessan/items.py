# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy



"""
price = Price(
    code=ticker,
    date=date,
    open=clean_numbers(out["始値"], is_int=False),
    high=clean_numbers(out["高値"], is_int=False),
    low=clean_numbers(out["安値"], is_int=False),
    close=clean_numbers(out["終値"], is_int=False),
    volume=max(clean_numbers(out['出来高']), clean_numbers(out['売買高(株)'])),
    n_transactions=clean_numbers(out["約定回数"]),
    transaction_amount=out["売買代金"],
    vwap=clean_numbers(out["VWAP"], is_int=False),
)

CREATE TABLE( 
code varchar(10),
date date,
open float,
high float,
low float,
close float,
volume float,
n_transactions int,
transaction_amount float,
vwap float,
mcap float,
)
"""

class KessanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    code = scrapy.Field()
    date = scrapy.Field()
    open = scrapy.Field()
    high = scrapy.Field()
    low = scrapy.Field()
    close = scrapy.Field()
    volume = scrapy.Field()

    n_transactions = scrapy.Field()
    transaction_amount = scrapy.Field()
    vwap = scrapy.Field()
    mcap = scrapy.Field()
