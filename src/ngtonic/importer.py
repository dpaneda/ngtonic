import csv
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

import xlrd  # type: ignore[import-untyped]
from dateutil import parser
from rich.console import Console

from .movements import Movement, Movements

console = Console()


class ImportSource(str, Enum):
    ing = "ing"
    revolut = "revolut"
    paypal = "paypal"


class Importer:
    """Class to import movements from different sources"""

    @staticmethod
    def import_files(source: ImportSource, files: list[Path]):
        movements = Movements.load()
        for path in files:
            if not path.is_file():
                console.print(f"[ERROR] The file {path} does not exists")
                continue
            match source:
                case ImportSource.ing:
                    new_movements = Importer.parse_ing_file(path)
                case ImportSource.revolut:
                    new_movements = Importer.parse_revolut_file(path)
                case ImportSource.paypal:
                    Importer.enrich_with_paypal(movements, path)
                    # No need to continue, the paypal method does everything
                    continue
                case _:
                    console.print(f"[ERROR] The source {source} is not supported")
                    return
            # Consume the movements from the generator
            added = 0
            for move in new_movements:
                if move not in movements.movements:
                    movements.movements.append(move)
                    added += 1
            console.print(f"Imported {added} movements from file {path} using {source.value} importer")
        movements.save()

    @staticmethod
    def parse_ing_file(file_name: Path):
        """Parse movements from an XLS file exported from ING"""
        book = xlrd.open_workbook(file_name)
        rows = book.sheet_by_index(0)
        # Very ugly way to do this and tied to spanish but not easy to do otherwise
        if [m.value for m in rows[3]] != [
            "F. VALOR",
            "CATEGORÍA",
            "SUBCATEGORÍA",
            "DESCRIPCIÓN",
            "COMENTARIO",
            "IMPORTE (€)",
            "SALDO (€)",
        ]:
            console.print(f"[ERROR] The file {file_name} does not seem to be a valid ING export")
            return

        for rx in range(rows.nrows):
            # Seek the movements
            cell = rows[rx]
            if cell[0].ctype != xlrd.XL_CELL_DATE:
                continue

            # Extract a date from the cell
            movement_date = xlrd.xldate.xldate_as_datetime(cell[0].value, 0).date()
            m = Movement(movement_date, cell[1].value, cell[2].value, cell[3].value, cell[5].value)
            yield m

    @staticmethod
    def parse_revolut_file(file_name: Path):
        """Parse movements from a CSV file exported from Revolut"""
        reader = csv.DictReader(file_name.open(), delimiter=",")
        for row in reader:
            if row["Type"] not in ("CARD_PAYMENT", "Card Payment"):
                # We are only interested in card payments
                continue
            movement_date = parser.parse(row["Started Date"]).date()
            yield Movement(movement_date, "Unknown", "Unknown", row["Description"], float(row["Amount"]))

    @staticmethod
    def enrich_with_paypal(movements: Movements, file_name: Path):
        """ "Enrich movements with PayPal information"""
        reader = csv.DictReader(file_name.open(encoding="utf-8-sig"), delimiter=",")
        paypal_movements = {}
        for row in reader:
            day = datetime.strptime(row["Date"], "%d/%m/%Y").date()  # noqa: DTZ007
            value = float(row["Amount"])
            if row["Status"] != "Completed" or not row["Name"]:
                # We are only interested in completed movements
                continue
            # The paypal transaction seems to be quite delayed sometimes
            for _ in range(6):
                paypal_movements[(day, value)] = row["Name"]
                day = day + timedelta(days=1)
        enriched_movements = 0
        for mv in movements.movements:
            if not mv.paypal_info and (mv.date, mv.value) in paypal_movements:
                mv.paypal_info = paypal_movements[(mv.date, mv.value)]
                enriched_movements += 1
        console.print(f"Enriched {enriched_movements} movements with PayPal information")
