# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

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

