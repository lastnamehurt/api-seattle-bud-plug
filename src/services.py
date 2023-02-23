import logging
import requests
import json
import pickle
from redis import Redis
from typing import Dict, List
from fastapi.encoders import jsonable_encoder


class SearchService:
    def __init__(self, location="Kemps") -> None:
        self.collection_items = {}
        self.raw_collection = {}
        self.parsed_items = []
        self.location = location
        self.url = "https://api.olla.co/v1/collections/?storeLocation=e6fc8d53-19ea-4ad6-9786-c85ba9381e7c&minimum&includeCollectionItems&limit=50&includeSalePrice"
        self.redis = Redis(host="localhost", port=6379, db=0)

        # Create a logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create a handler that writes logs to a file
        handler = logging.FileHandler("search_service.log")
        handler.setLevel(logging.DEBUG)

        # Create a formatter that adds a timestamp to each log message
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

    def get_collections(self):
        response = requests.get(self.url)
        collections = response.json().get("collections", [])
        return collections

    def fetch_collections(self):
        collections = self.get_collections()
        for collection in collections:
            data = collection.get("items", [])
            self.store_redis(collection["name"], json.dumps(data))
            self.collection_items[collection["name"]] = data
            self.raw_collection[collection["name"]] = collection
        self.logger.info("Fetched collections and stored in Redis.")

    def parse_item_to_deal(self, item):
        return SearchParser().parse(item)

    def parse_items(self):
        if not self.collection_items:
            self.fetch_collections()
        for brand, products in self.collection_items.items():
            for product in products:
                self.parsed_items.append(self.parse_item_to_deal(product))
        self.logger.info("Parsed items into deals.")
        return self.parsed_items

    def store_redis(self, key, value):
        pickled = pickle.dumps({key: value})
        self.redis.set(key, pickled)
        self.logger.info(f'Stored value in Redis for key "{key}".')

    def load_from_redis(self, item_name):
        item = self.redis.get(item_name)
        value = pickle.loads(item) if item is not None else None
        if value is not None:
            self.logger.info(f'Retrieved value from Redis for key "{item_name}".')
        else:
            self.logger.warning(f'Key "{item_name}" not found in Redis.')
        return value

    def run(self, use_cache=False):
        if use_cache:
            if not self.parsed_items:
                self.parse_items()
            self.logger.info("Retrieved parsed items from cache.")
            return self.parsed_items

        deals = []
        self.fetch_collections()
        for _, details in self.collection_items.items():
            for detail in details:
                deals.append(self.parse_item_to_deal(detail))
        self.logger.info("Fetched collections and parsed items into deals.")
        return deals


class SearchParser:
    def __init__(self):
        # Create a logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create a handler that writes logs to a file
        handler = logging.FileHandler("search_parser.log")
        handler.setLevel(logging.DEBUG)

        # Create a formatter that adds a timestamp to each log message
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

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
        self.logger.info(f"Parsed item {name} into deal: {parsed[name]}.")
        return parsed
