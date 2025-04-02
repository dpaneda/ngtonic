from rich.console import Console
from rich.table import Column, Table

from .bills import RegularBills
from .movements import Movements

console = Console()


class Printer:
    @staticmethod
    def list_movements_per_month(movements: Movements):
        table = Table(Column(header="Date", style="blue"), Column(header="Import (€)", justify="right", style="green"))
        movs_per_month = movements.get_movements_per_month()
        for k, v in movs_per_month.items():
            table.add_row(str(k), str(round(v, 2)))
        console.print(table)

    @staticmethod
    def list_movements(movements: Movements):
        table = Table(
            Column(header="Date", style="blue"),
            Column(header="Category", style="green"),
            Column(header="Subcategory", style="cyan"),
            Column(header="Description"),
            Column(header="Import (€)", justify="right", style="green"),
        )

        for m in movements.movements:
            description = m.description
            if m.paypal_info:
                description = f"Paypal ({m.paypal_info})"
            table.add_row(str(m.date), m.category, m.subcategory, description, str(m.value))
        console.print(table)
        console.print(f"Printed {len(table.rows)} movements")

    @staticmethod
    def list_bills(bills: RegularBills):
        table = Table(
            Column(header="First Date", style="blue"),
            Column(header="Last Date", style="blue"),
            Column(header="Category", style="green"),
            Column(header="Description"),
            Column(header="Hits"),
            Column(header="Last import (€)", justify="right", style="green"),
            Column(header="Total (€)", justify="right", style="green"),
        )

        for e in bills.bills.values():
            if e.ignore:
                continue
            table.add_row(
                str(e.start_date),
                str(e.info.date),
                e.info.category,
                e.info.description,
                str(e.hits),
                str(-round(e.info.value, 2)),
                str(-round(e.total, 2)),
            )
        console.print(table)
        console.print(f"Printed {len(table.rows)} fixed expenses")
