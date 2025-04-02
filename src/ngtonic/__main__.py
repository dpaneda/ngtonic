#! /usr/bin/env python

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .bills import RegularBills
from .importer import Importer, ImportSource
from .movements import MovementFilter, MovementFilterType, Movements
from .plotter import Plotter
from .printer import Printer

app = typer.Typer(no_args_is_help=True)
console = Console()


def abort(message: str):
    console.print(f"[ERROR] {message}", style="bold red")
    raise typer.Exit(1)


def load_and_filter_movements(categories, descriptions, incomes, expenses):
    m = Movements.load()
    if not m.movements:
        abort("The movements file is empty, you need to import some data first")

    movement_filters = []
    if categories:
        movement_filters += [MovementFilter(MovementFilterType.CATEGORY, value) for value in categories]
    if descriptions:
        movement_filters += [MovementFilter(MovementFilterType.DESCRIPTION, value) for value in descriptions]
    if incomes:
        movement_filters.append(MovementFilter(MovementFilterType.INCOME))
    if expenses:
        movement_filters.append(MovementFilter(MovementFilterType.EXPENSE))
    m.filter(movement_filters)

    if not m.movements:
        abort("You filter out all movements, chech your filters")
    return m


# Definition of some parameters shared in several functions
Category = Annotated[list[str] | None, typer.Option("--category", "-c", help="Filter by category")]
Description = Annotated[list[str] | None, typer.Option("--description", "-d", help="Filter by description")]
Incomes = Annotated[bool, typer.Option("--incomes", "-i", help="Show only incomes (positive transactions)")]
Expenses = Annotated[bool, typer.Option("--expenses", "-e", help="Show only incomes (positive transactions)")]
MonthGroup = Annotated[bool, typer.Option("--group-by-month", "-m", help="Group transactions by month")]
ConfigFile = Annotated[str, typer.Option("--config", "-o", help="Config file path")]


@app.command("import")
def import_movements(source: ImportSource, files: list[Path]):
    """Import movements files to the internal storage"""
    Importer.import_files(source, files)


@app.command("list")
def list_movements(
    categories: Category = None,
    descriptions: Description = None,
    incomes: Incomes = False,
    expenses: Expenses = False,
    month_group: MonthGroup = False,
):
    """Show a table listing the movements with optional filtering"""
    movements = load_and_filter_movements(categories, descriptions, incomes, expenses)
    if month_group:
        Printer.list_movements_per_month(movements)
    else:
        Printer.list_movements(movements)


@app.command()
def balance_plot(
    categories: Category = None,
    descriptions: Description = None,
    incomes: Incomes = False,
    expenses: Expenses = False,
):
    """Plot the evolution of the balance over time"""
    movements = load_and_filter_movements(categories, descriptions, incomes, expenses)
    Plotter.show_balance_over_time(movements)


@app.command()
def month_plot(
    categories: Category = None,
    descriptions: Description = None,
    incomes: Incomes = False,
    expenses: Expenses = False,
):
    """Plot the movements grouped per month"""
    movements = load_and_filter_movements(categories, descriptions, incomes, expenses)
    Plotter.show_movements_per_month(movements)


@app.command()
def find_bills():
    """Use a simple heuristic to find regular bills, like subscriptions"""
    movements = Movements.load()
    fe = RegularBills(movements)
    Printer.list_bills(fe)


if __name__ == "__main__":
    app()
