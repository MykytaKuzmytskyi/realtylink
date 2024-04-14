import time

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm


class HousesSpider(scrapy.Spider):
    name = "houses"
    allowed_domains = ["realtylink.org"]
    start_urls = ["https://realtylink.org/en/properties~for-rent"]

    def __init__(self, pages=3, **kwargs):
        super().__init__(**kwargs)
        self.pages = int(pages)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response: Response, **kwargs):
        for page in range(self.pages):
            body_unicode = response.body.decode('utf-8')
            selector = Selector(text=body_unicode)

            cards = selector.css("div.shell").getall()

            for card in tqdm(cards, desc=f"Page № {page + 1}"):
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
                data = self.get_images_and_descriptions(absolute_link)
                yield {
                    "link": absolute_link,
                    "title": title,
                    "price": price,
                    "region": region,
                    "address": address,
                    "rooms": num_rooms,
                    "area": area,
                    "image_urls": data["image_urls"],
                    "description": data["description"],
                }
            self.driver.get(response.url)
            time.sleep(1)

            next_button = self.driver.find_element(By.CLASS_NAME, "next")
            if next_button:
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(1)
                response = Response(url=self.driver.current_url, body=self.driver.page_source.encode('utf-8'))
            else:
                break

    def get_images_and_descriptions(self, absolute_link):
        self.driver.get(absolute_link)
        time.sleep(1)
        try:
            description_element = self.driver.find_element(By.CSS_SELECTOR, "div[itemprop='description']")
            description_text = description_element.get_attribute("innerHTML").strip()
        except NoSuchElementException:
            description_text = None

        next_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.summary-photos a[role='button']"))
        )

        self.driver.execute_script("arguments[0].click();", next_button)
        time.sleep(1)

        button = self.driver.find_element(By.CSS_SELECTOR, "div.wrap")
        image_urls = []

        for image_num in range(1, len(self.driver.find_elements(By.CSS_SELECTOR, "div.carousel > ul > li > img"))):
            image_urls.append(button.find_element(By.TAG_NAME, "img").get_attribute("src"))
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(button)
            )
            next_button.click()

        return {
            "description": description_text,
            "image_urls": image_urls,
        }

    def closed(self, reason):
        self.driver.quit()
