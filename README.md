# Book Store Scraping

This guide outlines the steps to create a web scraper using Scrapy to extract information from a book store website.

## Creating Scrapy Project and Spider 

1. **Create a Scrapy Project**
    ```sh
    scrapy startproject bookstore_scrapper
    ```

2. **Navigate to Spiders Directory**
    ```sh
    cd bookstore_scrapper/bookstore_scrapper/spiders
    ```

3. **Generate a New Spider**
    ```sh
    scrapy genspider bookspider books.toscrape.com
    ```

## Scrapy Shell

1. **Configure Scrapy for IPython Shell**
    - In the `scrapy.cfg` file, add the following line:
    - `shell = ipython`

2. **Open Scrapy Shell**
    ```sh
    scrapy shell
    ```

3. **Fetch the Website**
    ```sh
    fetch('https://books.toscrape.com/')
    ```

4. **View Response Object**
    ```sh
    response
    ```

5. **Select Books**
    ```sh
    books = response.css('article.product_pod')
    ```

6. **Choose the First Book**
    ```sh
    book = books[0]
    ```

7. **Extract Book Title**
   ```sh
   book.css("h3 a::text").get()
   ```

8. **Extract Book Price**
   ```sh
   book.css("p.price_color::text").get()
   ```

9. **Extract Book Availability**
   ```sh
   book.css("p.instock::text").getall()[1].strip()
   ```

10. **Extract Partial URL**
    ```sh
    book.css("h3 a").attrib['href']
    ```

11. **Exit**
    ```sh
    exit()
    ```

## Adding CSS Selectors to Spider 
1. Change the `bookspider.py` file:
   ```python
   def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            yield {
                'name': book.css("h3 a::text").get(),
                'price': book.css("p.price_color::text").get(),
                'availability': book.css("p.instock::text").getall()[1].strip(),
                'url': "https://books.toscrape.com/" + book.css("h3 a").attrib['href']
            }
   ```

2. Run the spider to scrape data:
   ```shell
   scrapy crawl bookspider -O myscrapeddata.json
   # To collect data in Json file format
   # Capital O indicates overwrite, small o indicates appending to the file
   ```

   ```shell
   scrapy crawl bookspider -O myscrapeddata.csv
   # To collect data in csv file format
   ```

3. Getting next page url 
   ```shell
   # response.css('li.next a').attrib['href']
   response.css('li.next a ::attr(href)').get()
   # If we use the first one and if we don't get any li next then it will return error 
   ```

4. New Parse Function

   ```python
   def parse(self, response):
     books = response.css('article.product_pod')
     for book in books:
         yield {
             'name': book.css("h3 a::text").get(),
             'price': book.css("p.price_color::text").get(),
             'availability': book.css("p.instock::text").getall()[1].strip(),
             'url': "https://books.toscrape.com/" + book.css("h3 a").attrib['href']
         }
   
     next_page_url = response.css('li.next a ::attr(href)').get()
     if next_page_url is not None :
         if 'catalogue' in next_page_url:
             next_page_url = "https://books.toscrape.com/" + next_page_url
         else:
             next_page_url = "https://books.toscrape.com/catalogue/" + next_page_url
         yield response.follow(next_page_url, callback=self.parse)
   ```
- `response.follow` indicates the URL that will be visited next, and `callback=self.parse` means that the response from that URL will be processed by the `parse` function.

## Get info from individual book page
1. **We need to change parse function**
   ```python
   import scrapy
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
     pass
   ```
   - `scrapy.Request` creates a new request to the URL stored in `book_url`.
   - `callback=self.parse_book_page` specifies that the response from `book_url` will be handled by the `parse_book_page` function.


2. **Scrapy shell for book page css selectors**
   - Title 
   ```sh
   response.css('div.product_main h1::text').get() 
   # 'In Her Wake'
   ```
   
   - Price
   ```sh
   response.css('p.price_color::text').get() 
   # '£12.84'
   ```
   
   - Description
   ```sh
   html = response 
   html.xpath('//div[@id="product_description"]/following-sibling::p/text()').get()
   #  'A perfect life … until she...'
   ```

   - Category 
   ```sh
   html = response 
   html.xpath('//li[@class="active"]/preceding-sibling::li[1]//a/text()').get()
   #  'Thriller'
   # html.xpath('//li[@class="active"]/preceding-sibling::li[1]//a/@href').get()
   # To get the url 
   ```
   
   - Table Data
   ```sh
   html = response 
   table_contents = html.css('table tr')
   # After adding get, it gets converted to str, so don't do it only in the end.
   upc = table_contents[0].css('td::text').get()
   product_type = table_contents[1].css('td::text').get()
   price_excluding_tax_ = table_contents[2].css('td::text').get()
   price_including_tax_ = table_contents[3].css('td::text').get()
   tax = table_contents[4].css('td::text').get()
   availability = table_contents[5].css('td::text').get()
   num_reviews = table_contents[6].css('td::text').get()
   #  'Thriller'
   # html.xpath('//li[@class="active"]/preceding-sibling::li[1]//a/@href').get()
   # To get the url 
   ```
   
   - Star Rating 
   ```sh
   html = response 
   html.xpath('//p[@class = "instock availability"]/following-sibling::p/@class').get()
   #  'star-rating One'
   ```

3. **Parse Book Function**
   ```python
   def parse_book_page(self, response):
     html = response
     table_contents = html.css('table tr')
     yield {
         'url' : response.url,
         'title' : html.css('div.product_main h1::text').get(),
         'upc' : table_contents[0].css('td::text').get(),
         'product_type' : table_contents[1].css('td::text').get(),
         'price_excluding_tax' : table_contents[2].css('td::text').get(),
         'price_including_tax' : table_contents[3].css('td::text').get(),
         'tax' : table_contents[4].css('td::text').get(),
         'availability' : table_contents[5].css('td::text').get(),
         'num_reviews' : table_contents[6].css('td::text').get(),
         'stars' : html.xpath('//p[@class = "instock availability"]/following-sibling::p/@class').get(),
         'category' : html.xpath('//li[@class="active"]/preceding-sibling::li[1]//a/text()').get(),
         'description' : html.xpath('//div[@id="product_description"]/following-sibling::p/text()').get(),
         'price' : html.css('p.price_color::text').get() 
     }
   ```
   
4. **Run Scrapy Crawl**
   ```sh
   scrapy crawl bookspider -O myscrapeddata.json
   ```

## Cleaning data using item and pipelines

1. **Creating Book Item Class:**
   - Include the following class in `items.py` file 
   - Do not include , after Field(), it is a major error
   ```python
   import scrapy
   class BookItem(scrapy.Item):
       url = scrapy.Field()
       title = scrapy.Field()
       upc = scrapy.Field()
       product_type = scrapy.Field()
       price_excluding_tax = scrapy.Field()
       price_including_tax = scrapy.Field()
       tax = scrapy.Field()
       availability = scrapy.Field()
       num_reviews = scrapy.Field()
       stars = scrapy.Field()
       category = scrapy.Field()
       description = scrapy.Field()
       price = scrapy.Field()
   ```

2. **Updating parse function** 
   ```python
   from ..items import BookItem
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
   ```

3. **Change in `pipelines.py`
   ```python
   class BookstoreScrapperPipeline:
       def process_item(self, item, spider):
           adapter = ItemAdapter(item)
   
           # Remove leading and trailing whitespace
           field_names = adapter.field_names()
           for field_name in field_names:
               adapter[field_name] = adapter.get(field_name).strip()
   
           # Category and product type to lower case
           to_lower = ['category', 'product_type']
           for field_name in to_lower:
               adapter[field_name] = adapter.get(field_name).lower()
   
           # price to float
           to_float = ['price_excluding_tax', 'price_including_tax', 'tax', 'price']
           for field_name in to_float:
               value = adapter.get(field_name)
               value = value.replace('£', '')
               adapter[field_name] = float(value)
   
           # number in stock
           value = adapter.get('availability')
           stock_list = value.split('(')
           if len(stock_list) < 2:
               adapter['availability'] = 0
           else:
               adapter['availability'] = int(stock_list[1].split(' ')[0])
   
           ## Reviews --> convert string to number
           adapter['num_reviews'] = int(adapter.get('num_reviews'))
   
           ## Stars --> convert text to number
           value = adapter.get('stars')
           star_list = value.split(' ')
           star_txt = star_list[1].lower()
           if star_txt == 'zero':
               adapter['stars'] = 0
           elif star_txt == 'one':
               adapter['stars'] = 1
           elif star_txt == 'two':
               adapter['stars'] = 2
           elif star_txt == 'three':
               adapter['stars'] = 3
           elif star_txt == 'four':
               adapter['stars'] = 4
           elif star_txt == 'five':
               adapter['stars'] = 5
   
           return item
   ```

4. **Change in settings**
   - Uncomment the following line in settings 
   ```python
   ITEM_PIPELINES = {
      "bookstore_scrapper.pipelines.BookstoreScrapperPipeline": 300,
   }
   ```         


