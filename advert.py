from dataclasses import dataclass, field
import enum


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
    bedrooms: int
    link: str
    description: str
