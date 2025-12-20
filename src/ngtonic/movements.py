from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path

import unidecode
import yaml
from fastclasses_json import dataclass_json
from rich.console import Console

config_path = Path("~/.ngtonic").expanduser()
movements_db = Path(f"{config_path}/movements.json")
user_config = Path(f"{config_path}/config.yaml")
console = Console()


@dataclass_json
@dataclass
class Movement:
    date: date
    category: str
    subcategory: str
    description: str
    value: float
    paypal_info: str | None = None


def fuzzy_match(needle, hay):
    def normalize(s):
        return unidecode.unidecode(s.lower())

    return normalize(needle) in normalize(hay)


class MovementFilterType(Enum):
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    DESCRIPTION = "description"
    INCOME = "income"
    EXPENSE = "expense"
    VALUE = "value"
    START_DATE = "start_date"
    END_DATE = "end_date"


@dataclass
class MovementFilter:
    filter_type: MovementFilterType
    filter_value: str | datetime | None = None

    def is_match(self, movement: Movement):  # noqa: PLR0911
        match self.filter_type:
            case MovementFilterType.CATEGORY:
                return fuzzy_match(self.filter_value, movement.category)
            case MovementFilterType.SUBCATEGORY:
                return fuzzy_match(self.filter_value, movement.subcategory)
            case MovementFilterType.DESCRIPTION:
                return fuzzy_match(self.filter_value, movement.description)
            case MovementFilterType.INCOME:
                return movement.value > 0
            case MovementFilterType.EXPENSE:
                return movement.value < 0
            case MovementFilterType.VALUE:
                return movement.value == float(self.filter_value)  # type: ignore[arg-type]
            case MovementFilterType.START_DATE:
                return movement.date >= self.filter_value.date()  # type: ignore[union-attr]
            case MovementFilterType.END_DATE:
                return movement.date <= self.filter_value.date()  # type: ignore[union-attr]
            case _:
                console.print(f"[ERROR] Unknown filter type: {self.filter_type}")
                return False


@dataclass_json
@dataclass
class Movements:
    movements: list[Movement]

    @staticmethod
    def load():
        if not movements_db.is_file():
            return Movements([])

        with movements_db.open() as f:
            return Movements.from_json(f.read())

    def save(self):
        self.sort()
        if not config_path.is_dir():
            config_path.mkdir()
        with movements_db.open("w+") as f:
            jm = self.to_json()
            f.write(jm)

    def filter(self, filters: list[MovementFilter]):
        self.movements = [m for m in self.movements if all(f.is_match(m) for f in filters)]

        if user_config.is_file():
            with user_config.open() as f:
                config = yaml.safe_load(f)
                if "excluded_movements" in config:
                    self.filter_exclusions(config["excluded_movements"])

        # Sort by date and calculate balance over time
        self.sort()

    def filter_exclusions(self, exclusions):
        def match_exclusion(exclusion, m):
            exclusion_filters = []
            for field, value in exclusion.items():
                exclusion_filters.append(MovementFilter(MovementFilterType(field), value))
            return all(f.is_match(m) for f in exclusion_filters)

        def should_exclude(m):
            return any(match_exclusion(e, m) for e in exclusions)

        self.movements = [m for m in self.movements if not should_exclude(m)]

    def sort(self):
        self.movements.sort(key=lambda m: m.date)

    def get_movements_per_month(self):
        movs_per_month = {}
        for m in self.movements:
            month = date(m.date.year, m.date.month, 1)
            if month not in movs_per_month:
                movs_per_month[month] = 0
            movs_per_month[month] += m.value
        return movs_per_month

    def get_balance_over_time(self):
        moves = {}
        n = 0
        for m in self.movements:
            n += m.value
            moves[m.date] = n
        return moves
