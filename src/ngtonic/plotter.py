from lazy_import import lazy_module  # type: ignore[import-untyped]

from .movements import Movements

# This module is very slow so we lazy load them instead
plt = lazy_module("matplotlib.pyplot")


def running_mean(values, window):
    # Not the fastest mean but faster than importing numpy :-|
    cumsum = [0]
    moving_aves = values[: window - 1]
    for i, n in enumerate(values, 1):
        cumsum.append(cumsum[i - 1] + n)
        if i >= window:
            moving_ave = (cumsum[i] - cumsum[i - window]) / window
            moving_aves.append(moving_ave)
    return moving_aves


class Plotter:
    @staticmethod
    def show_movements_per_month(movements: Movements):
        moves_per_month = movements.get_movements_per_month()
        x = moves_per_month.keys()
        y = list(moves_per_month.values())

        y_mean = running_mean(y, 5)
        _, ax = plt.subplots()
        ax.bar(x, y, width=25)
        plt.plot(x, y_mean, "r.-", label="Moving average")
        plt.xlabel("Time")
        plt.ylabel("Balance (€)")
        plt.title("Balance per month")
        plt.gcf().autofmt_xdate()
        plt.show()

    @staticmethod
    def show_balance_over_time(movements: Movements):
        moves_per_day = movements.get_balance_over_time()
        x = moves_per_day.keys()
        y = moves_per_day.values()

        _, ax = plt.subplots()
        ax.plot(x, y)
        ax.fill_between(x, y, alpha=0.5)
        ax.plot(x, y, color="k", linewidth=0.5)
        plt.xlabel("Time")
        plt.ylabel("Balance (€)")
        plt.title("Balance over time")
        plt.show()
