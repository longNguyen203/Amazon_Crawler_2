from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, Response
from typing import Any, Iterable

"""
    "https://sipwhiskey.com/collections/japanese-whisky"
    "https://sipwhiskey.com/collections/japanese-whisky/products/yamato-takeda-shingen-edition-mizunara-cask-japanese-whisky"
"""

class SipSpider(CrawlSpider):
    name = "SipShit"
    allowed_domains = ["sipwhiskey.com"]
    start_urls = ["https://sipwhiskey.com/"]
    
    rules = (
        Rule(LinkExtractor(allow="collections/japanese-whisky", deny="products")),
        Rule(LinkExtractor(allow="products"), callback="parse_items")
    )
    
    def parse(self, response: Response, **kwargs: Any) -> Any:
        return super().parse(response, **kwargs)
    
    def start_requests(self) -> Iterable[Request]:
        return super().start_requests()
    
    def parse_items(self, response):
        
        yield {
            "name": response.css("h1.title::text").get(),
            "price": response.css("h2.price-area span::text").get(),
            "brand": response.css("div.vendor a::text").get(),
            "stars": response.css("span.stamped-summary-text-1 strong::text").get(),
            "rating_count": "10"
        }