import re
import urllib.parse
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from rightmove_webscraper import RightmoveData
from zoopla import Zoopla

from house_search.advert import Advert, TransactionType, Website


class Location(Enum):

    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, zoopla: str, rightmove: str):
        self.zoopla = zoopla
        self.rightmove = rightmove

    CAMBRIDGE = "Cambridge, Cambridgeshire", "REGION^274"


class Filter(Enum):
    NO_SHARE = auto()


class Scraper(ABC):

    def get_cambridge_rentals(self) -> List[Advert]:
        return self.get_properties(Location.CAMBRIDGE, TransactionType.RENT, filters=[Filter.NO_SHARE])

    @abstractmethod
    def get_properties(
            self,
            location: Location,
            ttype: TransactionType,
            *,
            furnished: bool = False,
            filters: List[Filter] = None
    ) -> List[Advert]:
        pass


class RightMoveScraper(Scraper):

    def get_properties(
            self,
            location: Location,
            ttype: TransactionType,
            *,
            furnished: bool = False,
            filters: Optional[List[Filter]] = None
    ) -> List[Advert]:
        filters = filters or []
        params = {
            "locationIdentifier": location.rightmove,
            "propertyType": "bungalow,detached,flat,semi-detached,terraced",
            "includeLetAgreed": "false",
            "mustHave": "",
            "dontShow": "houseShare,retirement,student" if Filter.NO_SHARE in filters else "retirement",
            "keywords": ""
        }
        path = "property-to-rent" if ttype == TransactionType.RENT else "property-for-sale"
        url = f"https://www.rightmove.co.uk/{path}/find.html?{urllib.parse.urlencode(params)}"
        data = RightmoveData(url)
        adverts = []
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


class ZooplaAPIScraper(Scraper):

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_properties(
            self,
            location: Location,
            ttype: TransactionType,
            *,
            furnished: bool = False,
            filters: List[Filter] = None
    ) -> List[Advert]:
        filters = filters or []
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
        ] if Filter.NO_SHARE in filters else []
        while True:
            search = zoopla.property_listings({
                "listing_status": "rent" if ttype == TransactionType.RENT else "sale",
                "area": location.zoopla,
                "order_by": "price",
                "ordering": "ascending",
                "page_size": page_size,
                "page_number": page_num
            })
            for result in search.listing:
                if result.property_type in ['Parking/garage']:
                    continue
                if any(block in result.description.lower() for block in description_blocklist):
                    continue
                if Filter.NO_SHARE in filters and result.num_bathrooms < 1:
                    continue
                price = result.price
                if ttype == TransactionType.RENT:
                    price = result.price * 52 / 12  # API prices are per week
                adverts.append(Advert(
                    TransactionType.RENT if result.listing_status == "rent" else TransactionType.BUY,
                    Website.ZOOPLA,
                    price,
                    result.num_bedrooms,
                    result.details_url,
                    result.description
                ))
            if len(search.listing) == page_size:
                page_num += 1
            else:
                break
        return adverts


class ZooplaScraper(Scraper):

    def get_properties(
            self,
            location: Location,
            ttype: TransactionType,
            *,
            furnished: bool = False,
            filters: Optional[List[Filter]] = None
    ) -> List[Advert]:
        results = []
        page = 1
        while True:
            new_results = self.parse_page(location, ttype, page)
            if new_results:
                page += 1
                results += new_results
                continue
            break
        return results

    def parse_page(self, location: Location, ttype: TransactionType, page: int = 1):
        params = {
            "price_frequency": "per_month",
            "q": location.zoopla,
            "results_sort": "newest_listings",
            "search_source": "home",
            "page_size": 100,
            "pn": page
        }
        path = "/".join([x.strip().lower() for x in location.zoopla.split(",")][::-1])
        url = f"https://www.zoopla.co.uk/to-rent/property/{path}/?" + urllib.parse.urlencode(params)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "html.parser")
        results = []
        for results_listing in soup.select("ul.listing-results"):
            for result in results_listing.select(".listing-results-wrapper"):
                result_info = result.select_one(".listing-results-right")
                price_tag = result_info.select_one(".text-price")
                num_beds = result_info.select_one(".num-beds")
                desc_preview = result_info.select("p")  # ?
                price = int(re.compile(r"£([0-9,]+) pcm").search(price_tag.text.strip()).group(1).replace(",", ""))
                results.append(Advert(
                    ttype,
                    Website.ZOOPLA,
                    price,
                    int(num_beds.text) if num_beds is not None else None,
                    "https://zoopla.co.uk/" + price_tag['href'].split("?")[0],
                    max([x.text.strip() for x in desc_preview])
                ))
        return results
