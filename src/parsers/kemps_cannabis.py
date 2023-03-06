import logging


class KempsCannabisParser:
    def __init__(self):
        # Create a logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create a handler that writes logs to a file
        handler = logging.FileHandler("./src/logs/kemps_cannabis_parser.log")
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
        image = item["price"]["product"]["default_image"]
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
            "image": image
        }
        self.logger.info(f"Parsed item {name} into deal: {parsed[name]}.")
        return parsed
