from dataclasses import dataclass, field
import enum
from datetime import datetime
from typing import Optional, List


class TransactionType(enum.Enum):
    RENT = enum.auto()
    BUY = enum.auto()


class Website(enum.Enum):
    ZOOPLA = enum.auto()
    RIGHTMOVE = enum.auto()


@dataclass
class Advert:
    transaction_type: TransactionType = field(repr=False)
    website: Website = field(repr=False)
    price: int
    bedrooms: Optional[int]
    link: str
    description: Optional[str]

    @property
    def advert_id(self) -> str:
        return self.link


class FullAdvert(Advert):
    bedrooms: int
    description: str


@dataclass
class AdvertRecord:
    first_seen: datetime
    advert_history: List[Advert]
    _last_seen: Optional[datetime] = None
    removed: bool = False

    @property
    def last_seen(self) -> datetime:
        return self._last_seen

    @last_seen.setter
    def last_seen(self, last_seen: datetime):
        self._last_seen = last_seen

    @property
    def record_id(self) -> str:
        return self.advert_history[-1].advert_id
