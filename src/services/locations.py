locations = {
    "e6fc8d53-19ea-4ad6-9786-c85ba9381e7c": "Kemp's Cannabis, Belltown",
}


class LocationsMapper:
    
    locations_map = locations
    
    def get_location_id_by_name(name):
        names = list(locations.values())
        inverted = {v: k for k, v in locations.items()}
        for _name in names:
            if name in _name.split():
                return inverted[_name]



