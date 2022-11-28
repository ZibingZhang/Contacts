import dataclasses
import enum

from common.utils import dataclasses_utils
from model import date_field


class Country(str, enum.Enum):
    UNITED_STATES = "United States"


class CountryCode(int, enum.Enum):
    NANP = 1
    IRELAND = 353
    UNITED_KINGDOM = 44
    BRAZIL = 55
    CHILE = 56
    HONG_KONG = 852
    CHINA = 86
    TAIWAN = 886


@dataclasses.dataclass
class Date(dataclasses_utils.DataClassJsonMixin):
    day: int | None = None
    month: int | None = None
    year: int | None = None


@dataclasses.dataclass
class DateRange(dataclasses_utils.DataClassJsonMixin):
    start: Date | None = date_field.new_field(required=False)
    end: Date | None = date_field.new_field(required=False)
