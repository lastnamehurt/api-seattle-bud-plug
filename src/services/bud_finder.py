import logging
import pickle

import requests
from redis import Redis

from src.parsers.kemps_cannabis import KempsCannabisParser


class BudFinder:
    API_URL = "https://api.olla.co/v1/collections/?storeLocation=e6fc8d53-19ea-4ad6-9786-c85ba9381e7c&minimum&includeCollectionItems&limit=50&includeSalePrice"

    def __init__(self, location: str = "Kemps") -> None:
        self.raw_collection = {}
        self.parsed_items = []
        self.location = location
        self.url = BudFinder.API_URL
        self.redis = Redis(host="localhost", port=6379, db=0)

        self._configure_logger()

    def _configure_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler("bud_finder.log")
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def fetch_collections(self):
        self.logger.info("Fetching collections")
        response = requests.get(self.url)

        self.logger.info(
            f"Finished fetching collections. Status code: '{response.status_code}'")

        data = response.json().get("collections", [])

        if data:
            self.store_to_redis(self.location, data)
            self.raw_collection = data

        self.normalize_redis_store_to_parsed_items()

        return data

    def parse_collections(self, collections=None):
        if collections is None:
            collections = self.retrieve_from_redis(self.location)

        if not collections:
            collections = self.fetch_collections()

        for collection in collections:
            self.parse_collection(collection)
            # self.store_redis(collection['name'], collection)

        return self.parsed_items

    def store_to_redis(self, key, value):
        return self.redis.set(key, pickle.dumps(value))

    def retrieve_from_redis(self, key):
        return pickle.loads(self.redis.get(key))

    def normalize_redis_store_to_parsed_items(self):
        locations_store = self.get_redis_store()
        self.parsed_items = []

        for location in locations_store:
            collections = location['value']

            # parse collections
            for collection in collections:
                self.parse_collection(collection)

        return self.parsed_items

    def get_collection_items(self, collection):
        return collection.get('items', [])

    def parse_collection(self, collection):
        items = self.get_collection_items(collection)
        for item in items:
            parsed = self.parse(item)
            # self.store_to_redis(item['price']['queue_name'], parsed)

        return self.parsed_items

    def get_redis_store(self):
        keys = self.redis.keys("*")
        values = []
        for key in keys:
            value = self.retrieve_from_redis(key)
            values.append({"key": key.decode(), "value": value})
        self.logger.info("Retrieved all values from Redis.")
        return values

    def parse(self, item):
        parsed = KempsCannabisParser().parse(item)
        self.parsed_items.append(parsed)
        return parsed

    def run(self, use_cache=False):
        if use_cache:
            if not self.parsed_items:
                self.normalize_redis_store_to_parsed_items()
            self.logger.info(f"Retrieved parsed items from cache.")
            return self.parsed_items

        self.fetch_collections()
        self.logger.info(f"Fetched collections and parsed items into deals.")

        return self.parsed_items
