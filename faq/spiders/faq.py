import scrapy
import bs4


class FaqSpider(scrapy.Spider):
    name = "faq"
    # allowed_domains = [""]
    start_urls = ["https://faq.wistronits.com/redmine/projects/portaltp/wiki/"]

    def parse(self, response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        titles = soup.find_all('a', {'name': 'post_title'})
        for title in titles:
            print(title.text.strip())
