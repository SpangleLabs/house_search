from dataclasses import dataclass
import enum


class TransactionType(enum.Enum):
    RENT = enum.auto()
    BUY = enum.auto()


class Website(enum.Enum):
    ZOOPLA = enum.auto()
    RIGHTMOVE = enum.auto()


@dataclass
class Advert:
    transaction_type: TransactionType
    website: Website
    price: int
    bedrooms: int
    link: str
    description: str
