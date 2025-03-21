from dataclasses import dataclass
from datetime import date
from pathlib import Path

import unidecode
import xlrd  # type: ignore[import-untyped]
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


def fuzzy_match(needle, hay):
    def normalize(s):
        return unidecode.unidecode(s.lower())

    return normalize(needle) in normalize(hay)


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

    def filter(self, category: list[str] | None, description: list[str] | None, incomes: bool, expenses: bool):
        if description is None:
            description = []
        if category is None:
            category = []

        for needle in category:
            self.filter_by_field("category", needle)
        for needle in description:
            self.filter_by_field("description", needle)
        if incomes:
            self.filter_incomes()
        if expenses:
            self.filter_expenses()

        if user_config.is_file():
            with user_config.open() as f:
                config = yaml.safe_load(f)
                self.filter_exclusions(config["excluded_movements"])

        # Sort by date and calculate balance over time
        self.sort()

    @staticmethod
    def import_files(files: list[Path]):
        movements = Movements.load()
        for path in files:
            if path.is_file():
                n = movements.import_from_ing(path)
                console.print(f"Imported {n} movements from file {path}")
            else:
                console.print(f"[ERROR] The file {path} does not exists")
        movements.save()

    def import_from_ing(self, file_name: Path) -> int:
        book = xlrd.open_workbook(file_name)
        sh = book.sheet_by_index(0)
        initial_size = len(self.movements)
        for rx in range(sh.nrows):
            # Seek the movements
            cell = sh[rx]
            if cell[0].ctype != xlrd.XL_CELL_DATE:
                continue

            # Extract a date from the cell
            dt = xlrd.xldate.xldate_as_datetime(cell[0].value, 0).date()
            move = Movement(dt, cell[1].value, cell[2].value, cell[3].value, cell[6].value)

            # Skip duplicated movement
            if move in self.movements:
                continue
            self.movements.append(move)
        return len(self.movements) - initial_size

    def filter_by_field(self, field, needle):
        self.movements = [m for m in self.movements if fuzzy_match(needle, getattr(m, field))]

    def filter_incomes(self):
        self.movements = [m for m in self.movements if m.value > 0]

    def filter_expenses(self):
        self.movements = [m for m in self.movements if m.value < 0]

    def filter_exclusions(self, exclusions):
        def match_exclusion(exclusion, m):
            for field, value in exclusion.items():
                match field:
                    case "category" | "subcategory" | "description":
                        if not fuzzy_match(value, getattr(m, field)):
                            return False
                    case "value":
                        if value != m.value:
                            return False
            return True

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
