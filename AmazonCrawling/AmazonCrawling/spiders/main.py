# from typing import Iterable, Any
# from scrapy.http import Request, Response
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor
# from scrapy import Request
# from urllib.parse import urljoin
# import json
# import re


# class CrawlingSpider(CrawlSpider):
#     name = "MyCrawlerData"
    
#     def start_requests(self):
#         keyword_search = "Ipad"
#         for page in range(1, 5):
#             amazon_search_url = f'https://www.amazon.com/s?k={keyword_search}&page={page}'
#             yield Request(url=amazon_search_url, callback=self.discover_product_urls)
    
#     def discover_product_urls(self, response):
#         search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
#         for product in search_products:
#             relative_url = product.css("h2>a::attr(href)").get()
#             product_url = urljoin('https://www.amazon.com/', relative_url).split("?")[0]
#             yield Request(url=product_url, callback=self.parse_product_data)
            
#         ## Get All Pages
#         available_pages = response.xpath(
#             '//*[contains(@class, "s-pagination-item")][not(has-class("s-pagination-separator"))]/text()'
#         ).getall()

#         last_page = available_pages[-1]
#         for page_num in range(2, int(last_page)):
#             amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page={page_num}'
#             yield Request(url=amazon_search_url, callback=self.parse_search_results)

    
#     def parse_product_data(self, response):
#         price = response.css('.a-price span[aria-hidden="true"] ::text').get("")
#         if not price:
#             price = response.css('.a-price .a-offscreen ::text').get("")
#         yield {
#             "name": response.css("#productTitle::text").get("").strip(),
#             "price": price,
#             "stars": response.css("i[data-hook=average-star-rating] ::text").get("").strip(),
#             "rating_count": response.css("div[data-hook=total-review-count] ::text").get("").strip(),
#         }
            
    # def parse_item(self, response):
    #     yield {
    #         "name": response.css("h1::text").get(),
    #         "price": response.css(),
    #         "stars": response.css(),
    #         "rating_count": response.css(),
    #         "feature_bullets": response.css(),
    #         "images": response.css(),
    #         "variant_data": response.css()
    #     }
        
    
    # def start_requests(self) -> Iterable[Request]:
    #     return super().start_requests()
    
    # def parse(self, response: Response, **kwargs: Any) -> Any:
    #     return super().parse(response, **kwargs)
    

import scrapy
from urllib.parse import urljoin

class AmazonReviewsSpider(scrapy.Spider):
    name = "amazon_reviews"

    def start_requests(self):
        asin_list = ['B09G9FPHY6']
        for asin in asin_list:
            amazon_reviews_url = f'https://www.amazon.com/product-reviews/{asin}/'
            yield scrapy.Request(url=amazon_reviews_url, callback=self.parse_reviews, meta={'asin': asin, 'retry_count': 0})


    def parse_reviews(self, response):
        asin = response.meta['asin']
        retry_count = response.meta['retry_count']

        ## Get Next Page Url
        next_page_relative_url = response.css(".a-pagination .a-last>a::attr(href)").get()
        if next_page_relative_url is not None:
            retry_count = 0
            next_page = urljoin('https://www.amazon.com/', next_page_relative_url)
            yield scrapy.Request(url=next_page, callback=self.parse_reviews, meta={'asin': asin, 'retry_count': retry_count})
        
        ## Adding this retry_count here to bypass any amazon js rendered review pages
        elif retry_count < 3:
            retry_count = retry_count+1
            yield scrapy.Request(url=response.url, callback=self.parse_reviews, dont_filter=True, meta={'asin': asin, 'retry_count': retry_count})

        ## Parse Product Reviews
        review_elements = response.css("#cm_cr-review_list div.review")
        for review_element in review_elements:
            yield {
                    "asin": asin,
                    "text": "".join(review_element.css("span[data-hook=review-body] ::text").getall()).strip(),
                    "title": review_element.css("*[data-hook=review-title]>span::text").get(),
                    "location_and_date": review_element.css("span[data-hook=review-date] ::text").get(),
                    "verified": bool(review_element.css("span[data-hook=avp-badge] ::text").get()),
                    "rating": review_element.css("*[data-hook*=review-star-rating] ::text").re(r"(\d+\.*\d*) out")[0],
                    }


    