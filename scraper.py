from abc import ABC, abstractmethod
from typing import List

from rightmove_webscraper import RightmoveData
from zoopla import Zoopla

from advert import Advert, TransactionType, Website


class Scraper(ABC):

    @abstractmethod
    def get_cambridge_rentals(self) -> List[Advert]:
        pass


class RightMoveScraper(Scraper):

    def get_cambridge_rentals(self) -> List[Advert]:
        url = f"https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E274&propertyTypes=bungalow%2Cdetached%2Cflat%2Csemi-detached%2Cterraced&includeLetAgreed=false&mustHave=&dontShow=houseShare%2Cretirement%2Cstudent&furnishTypes=unfurnished&keywords="
        data = RightmoveData(url)
        adverts = []
        ttype = TransactionType.RENT if data.rent_or_sale == "rent" else TransactionType.BUY
        for ad in data.get_results.iterrows():
            adverts.append(Advert(
                ttype,
                Website.RIGHTMOVE,
                ad[1].price,
                ad[1].number_bedrooms,
                ad[1].url,
                ""  # TODO
            ))
        return adverts


class ZooplaScraper(Scraper):

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_cambridge_rentals(self) -> List[Advert]:
        zoopla = Zoopla(self.api_key)
        page_size = 100
        page_num = 1
        adverts = []
        description_blocklist = [
            "communal bathroom", "communal kitchen", "communal areas",
            "communal living room", "house share", "shared house",
            "communal entrance hall", "single room", "this room",
            "communal space", "communal study", "room available",
            "communal cleaner", "rooms available", "per person",
            "sharing", "shared", "sharer", "student accommodation"
        ]
        search = zoopla.property_listings({
            "listing_status": "rent",
            "area": "Cambridge, Cambridgeshire",
            "minimum_beds": 2,
            "order_by": "price",
            "ordering": "ascending",
            "page_size": page_size,
            "page_number": page_num
        })
        while True:
            for result in search.listing:
                if result.property_type in ['Parking/garage']:
                    continue
                if any(block in result.description.lower() for block in description_blocklist):
                    continue
                if result.num_bathrooms < 1:
                    continue
                adverts.append(Advert(
                    TransactionType.RENT if result.listing_status == "rent" else TransactionType.BUY,
                    Website.ZOOPLA,
                    result.price * 52 / 12,  # API prices are per week
                    result.num_bedrooms,
                    result.details_url,
                    result.description
                ))
            if len(search.listing) == page_size:
                page_num += 1
            else:
                break
        return adverts
