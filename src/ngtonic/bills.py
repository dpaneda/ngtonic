import datetime
from dataclasses import dataclass

from rich.console import Console

from .movements import Movement, Movements

console = Console()


@dataclass
class RegularBill:
    info: Movement  # Store last movement for common information
    start_date: datetime.date
    hits: int
    total: float
    ignore: bool = False


@dataclass
class RegularBills:
    """This class implements a very simplistic heuristic to try to find regular bills"""

    bills: dict[str, RegularBill]

    def __init__(self, moves: Movements):
        def valid_expense(e):
            period = (e.info.date - e.start_date) / e.hits
            return 22 < period.days < 32 and not e.ignore  # noqa: PLR2004

        moves.movements = [m for m in moves.movements if m.value < 0]
        moves.sort()
        expenses = {}

        for m in moves.movements:
            if m.description not in expenses:
                expenses[m.description] = RegularBill(m, m.date, 1, m.value)
            else:
                e = expenses[m.description]
                if e.hits == 1 and m.value != e.info.value:
                    e.ignore = True
                e.hits += 1
                e.info = m
                e.total += m.value

        self.bills = {k: v for (k, v) in expenses.items() if valid_expense(v)}
