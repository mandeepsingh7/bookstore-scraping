import scrapy
from ..items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            partial_url = book.css("h3 a ::attr(href)").get()
            if 'catalogue' in partial_url:
                book_url = "https://books.toscrape.com/" + partial_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + partial_url
            yield scrapy.Request(book_url, callback=self.parse_book_page)

        next_page_url = response.css('li.next a ::attr(href)').get()
        if next_page_url is not None :
            if 'catalogue' in next_page_url:
                next_page_url = "https://books.toscrape.com/" + next_page_url
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page_url
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        html = response
        table_contents = html.css('table tr')

        book_item = BookItem()
        book_item['url'] = response.url
        book_item['title'] = html.css('div.product_main h1::text').get()
        book_item['upc'] = table_contents[0].css('td::text').get()
        book_item['product_type'] = table_contents[1].css('td::text').get()
        book_item['price_excluding_tax'] = table_contents[2].css('td::text').get()
        book_item['price_including_tax'] = table_contents[3].css('td::text').get()
        book_item['tax'] = table_contents[4].css('td::text').get()
        book_item['availability'] = table_contents[5].css('td::text').get()
        book_item['num_reviews'] = table_contents[6].css('td::text').get()
        book_item['stars'] = html.xpath('//p[@class = "instock availability"]/following-sibling::p/@class').get()
        book_item['category'] = html.xpath('//li[@class="active"]/preceding-sibling::li[1]//a/text()').get()
        book_item['description'] = html.xpath('//div[@id="product_description"]/following-sibling::p/text()').get()
        book_item['price'] = html.css('p.price_color::text').get()
        yield book_item