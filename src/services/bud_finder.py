import logging
import os
import pickle

import redis
import requests

from src.parsers.kemps_cannabis import KempsCannabisParser
from src.services.locations import LocationsMapper

redis_url = os.environ.get(
    "REDIS_URL",
    "redis://:pe0c9599ef23a3ef81ec5489038a1b9225b7fa21adf5c7aff295dc2cc32b88e0c@ec2-44-205-74-123.compute-1.amazonaws.com:26119",
)
redis_client = redis.from_url(redis_url)
default_location_id = list(LocationsMapper.locations_map.keys())[0]

class BudFinder:

    def __init__(self, location: str = "Belltown", location_id=default_location_id) -> None:
        self.raw_collection = {}
        self.parsed_items = []
        self.location = location
        self.location_id = location_id
        self.url = f"https://api.olla.co/v1/collections/?storeLocation={location_id}&minimum&includeCollectionItems&limit=50&includeSalePrice"
        self.redis = redis_client

        self._configure_logger()

    def _configure_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler("./src/logs/bud_finder.log")
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
            self.store_to_redis(LocationsMapper.locations_map[self.location_id], data)
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
        self.logger.info(f"Storing {key} to Redis.")
        return self.redis.set(key, pickle.dumps(value))

    def retrieve_from_redis(self, key):
        try:
            value = pickle.loads(self.redis.get(key))
            self.logger.info(f"Retrieved {key} from Redis.")
            return value
        except Exception as error:
            self.logger.error(f"Error retrieving {key} from Redis: {error}")
            raise error

    def normalize_redis_store_to_parsed_items(self):
        self.parsed_items = []
        locations_store = self.get_redis_store()

        if len(locations_store) == 0:
            return {}
        
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
