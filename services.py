import os
import json
import requests
import redis
import pickle

redis_url = os.environ.get(
    "REDIS_URL",
    f"{os.environ.get('REDISURL', '')}:26120",
)
redis_client = redis.from_url(redis_url)


class SearchService:
    def __init__(self, location="Kemps") -> None:
        self.collection_items = {}
        self.raw_collection = {}
        self.parsed_items = []
        self.location = location
        self.url = "https://api.olla.co/v1/collections/?storeLocation=e6fc8d53-19ea-4ad6-9786-c85ba9381e7c&minimum&includeCollectionItems&limit=50&includeSalePrice"
        self.redis = redis_client

    def get_collections(self):
        return requests.get(self.url).json()["collections"]

    def fetch_collections(self):
        collections = self.get_collections()
        for collection in collections:
            data = collection["items"]
            self.store_redis(collection["name"], json.dumps(data))
            self.collection_items[collection["name"]] = collection["items"]
            self.raw_collection[collection["name"]] = collection

    def parse_item_to_deal(self, item):
        return SearchParser().parse(item)

    def parse_items(self):
        if not self.collection_items:
            self.fetch_collections()
        for brand, products in self.collection_items.items():
            for product in products:
                self.parsed_items.append(self.parse_item_to_deal(product))
        return self.parsed_items

    def store_redis(self, key, value):
        pickled = pickle.dumps({key: value})
        return self.redis.set(key, pickled)

    def load_from_redis(self, item_name):
        item = self.redis.get(item_name)
        return pickle.loads(item)

    def run(self, use_cache=False):
        if use_cache:
            if not self.parsed_items:
                self.parse_items()

            return self.parsed_items

        deals = []
        self.fetch_collections()
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
        name = item["price"]["product"]["name"]
        brand = item["price"]["product"]["brand"]
        sale_price = item["sale_usd"]
        amount_in_stock = item["price"]["amount_in_stock"]
        weight = item["price"]["weight"]
        thc_percentage = item["price"]["thc_percentage"]
        cbd_percentage = item["price"]["cbd_percentage"]
        category = item["price"]["product"]["subcategory"]["category"]["name"]
        item_type = item["price"]["product"]["subcategory"]["name"]
        location_id = item["price"]["store_location_id"]
        parsed[name] = {
            "id": item["id"],
            "name": name,
            "brand": brand,
            "price": sale_price,
            "url": self.build_url(name, brand, item["price"]["product"]["product_id"]),
            "amount_in_stock": amount_in_stock,
            "thc_percentage": thc_percentage,
            "cbd_percentage": cbd_percentage,
            "weight": weight,
            "category": category,
            "type": item_type,
            "location_id": location_id,
        }
        return parsed
