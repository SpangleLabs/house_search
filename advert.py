from dataclasses import dataclass, field
import enum
from typing import Optional


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


class FullAdvert(Advert):
    bedrooms: int
    description: str
