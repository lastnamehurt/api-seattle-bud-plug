
class BudFinder(object):
    def __init__(self, location="") -> None:
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

        def fetch_products():
            pass

        def parse_to_plug_offer():
            pass