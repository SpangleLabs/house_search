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
        search = zoopla.property_listings({
            "listing_status": "rent",
            "area": "Cambridge, Cambridgeshire"
        })
        adverts = []
        for result in search.listing:
            adverts.append(Advert(
                TransactionType.RENT if result.listing_status == "rent" else TransactionType.BUY,
                Website.ZOOPLA,
                result.price * 52 / 12,  # API prices are per week
                result.num_bedrooms,
                result.details_url,
                result.description
            ))
        return adverts
