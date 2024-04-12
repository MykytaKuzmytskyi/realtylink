import scrapy
from scrapy import Selector
from scrapy.http import Response


class HousesSpider(scrapy.Spider):
    name = "houses"
    allowed_domains = ["realtylink.org"]
    start_urls = ["https://realtylink.org/en/properties~for-rent"]

    def parse(self, response: Response, **kwargs):
        cards = response.css("div.shell").getall()

        for card in cards:
            selector = Selector(text=card)

            link = selector.css('.a-more-detail::attr(href)').get()
            absolute_link = response.urljoin(link) if link else None

            title = selector.css('span.category div::text').get().strip()
            price = selector.css('div.price span::text').get().strip()
            region = selector.css("span.address div:nth-child(2)::text").get()
            address = ', '.join(selector.css("span.address div::text").getall())
            rooms_str = selector.css("div.cac::text").get()
            num_rooms = int(rooms_str) if rooms_str else 1

            area = selector.css("span.sqft span::text").get()

            yield {
                "link": absolute_link,
                "title": title,
                "price": price,
                "region": region,
                "address": address,
                "rooms": num_rooms,
                "area": area,
            }
