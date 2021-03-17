import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from oberbankde.items import Article


class OberbankdeSpider(scrapy.Spider):
    name = 'oberbankde'
    start_urls = ['https://www.oberbank.de/newsroom']

    def parse(self, response):
        links = response.xpath('//a[@class="dt-a-arrow"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="dt-pre-headline"]/text()').get()
        if date:
            date = date.strip().split()[0]

        content = response.xpath('//div[@class="col-sm-12 col-md-9"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
