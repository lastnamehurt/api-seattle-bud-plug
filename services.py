import os
import requests
import redis 
import pickle

redis_url = os.environ.get("redis://redis:6379", "redis://redis:6379")
redis_client = redis.from_url(redis_url)

class SearchService:

    def __init__(self, location = "Kemps") -> None:
        self.collection_items = {}
        self.location = location
        self.url = "https://api.olla.co/v1/collections/?storeLocation=e6fc8d53-19ea-4ad6-9786-c85ba9381e7c&minimum&includeCollectionItems&limit=50&includeSalePrice"
        self.redis = redis_client

    def get_collections(self):
        return requests.get(self.url).json()['collections']

    def get_collection_items(self):
        collections = self.get_collections()
        for collection in collections:
            self.collection_items[collection['name']] = collection['items']
            self.store_redis(collection)
    
    def parse_item_to_deal(self, item):
        return SearchParser().parse(item)

    def store_redis(self, item):
        pickled = pickle.dumps(item)
        return self.redis.set(item['name'], pickled)

    def load_from_redis(self, item_name):
        pickled = self.redis.get(item_name)
        item = pickle.loads(pickled)
        return item 

    def run(self):
        deals = []
        self.get_collection_items()
        for _, details in self.collection_items.items():
            for detail in details:
                deals.append(self.parse_item_to_deal(detail))
        return deals


class SearchParser:

    def build_url(self, product_name, product_brand, product_id):
        product_name = "_".join(product_name.split())
        product_brand = "_".join(product_brand.split())
        return f"https://shop.kempscannabis.com/seattle/brand/{product_brand}/product/{product_name}?id={product_id}"
        
    def parse(self, item):
        parsed = {}
        name = item['price']['product']['name']
        brand = item['price']['product']['brand']
        sale_price = item['sale_usd']
        amount_in_stock = item['price']['amount_in_stock']
        weight = item['price']['weight']
        thc_percentage = item['price']['thc_percentage']
        cbd_percentage = item['price']['cbd_percentage']
        category = item['price']['product']['subcategory']['category']['name']
        item_type = item['price']['product']['subcategory']['name']
        parsed[name] = {
            'brand': brand,
            'price': sale_price,
            'url': self.build_url(name, brand, item['price']['product']['product_id']),
            'amount_in_stock': amount_in_stock,
            'thc_percentage': thc_percentage,
            'cbd_percentage': cbd_percentage,
            'weight': weight,
            'category': category,
            'type': item_type
        }
        return parsed
