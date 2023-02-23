class DISPENSARY_LOCATION_ID:
    KEMPS_CANNABIS_DOWNTOWN = "e6fc8d53-19ea-4ad6-9786-c85ba9381e7c"
    KEMPS_CANNABIS_SODO = ""
    THE_BAKEREE = ""


class DISPENSARY_ENDPOINT(object):
    KEMPS_CANNABIS_DOWNTOWN = f"https://api.olla.co/v1/collections/?storeLocation={DISPENSARY_LOCATION_ID.KEMPS_CANNABIS_DOWNTOWN}&minimum&includeCollectionItems&limit=50&includeSalePrice"
    KEMPS_CANNABIS_SODO = f"https://api.olla.co/v1/collections/?storeLocation={DISPENSARY_LOCATION_ID.KEMPS_CANNABIS_SODO}&minimum&includeCollectionItems&limit=50&includeSalePrice"


CONFIG = {
    "REDIS_URL": "redis://:pe0c9599ef23a3ef81ec5489038a1b9225b7fa21adf5c7aff295dc2cc32b88e0c@ec2-44-205-74-123.compute-1.amazonaws.com:26119"
}
