<h1 align="center">ngtonic</h1>
<h3 align="center">Personal finances on your terminal</h2>

<p align="center">
<a href="https://pypi.org/project/ngtonic/">
<img alt="CI" src="https://img.shields.io/pypi/v/ngtonic?logo=pypi&logoColor=white">
</a>
<img alt="PyPI - License" src="https://img.shields.io/pypi/l/ngtonic">
<img alt="Linux" src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black">
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/ngtonic">
</p>

## 🌟 Motivation and Description

Ngtonic is a small tool created to manage personal finances directly from the terminal, avoiding the need to share sensitive financial data with third-party apps. It's tailored for my specific needs. Currently, Ngtonic only supports ING bank, leveraging its automatic categorization of movements.

I also created it as an example of building a project "the right way" on GitHub.

## 🤔 Why Use Ngtonic?

Consider using Ngtonic if you:

 - Prefer not to use apps like Fintonic
 - Primarily use ING for personal expenses
 - Want a simple, terminal-based tool to check your finances
 - Value privacy and keeping your financial data local

For those seeking more advanced features or a GUI, [Firefly III](https://www.firefly-iii.org) might be a better option.

## 👨‍💻 Getting started

1. Install using [pipx](https://pipx.pypa.io/stable/installation/) (recommended) or pip:

```bash
pipx install ngtonic
```

2. Download your ING account movements as an Excel file.

3. Import the movements:

```bash
ngtonic import ing movements.xls
```

Your data is now stored locally in `.ngtonic/movements.json`. You can import multiple files; Ngtonic will automatically deduplicate the data.

## 📊 Usage

Ngtonic offers several commands:

```
╭─ Commands ──────────────────────────────────────────────────────────────────────╮
│ import         Import movements files to the internal storage                   │
│ list           Show a table listing the movements with optional filtering       │
│ balance-plot   Plot the evolution of the balance over time                      │
│ month-plot     Plot the movements grouped per month                             │
│ find-bills     Use a simple heuristic to find regular bills, like subscriptions │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

```bash
# Use category filtering to list home expenses
ngtonic list -c hogar

# List leisure expenses by month
ngtonic list -c ocio -m

# Check Steam purchases by month
ngtonic list -d steam -m

# Use the integrated heuristic to find regular bills
ngtonic find-bills
```
The plot commands enable you to visualize movements grouped by month or track the balance over time. You can apply the same filters available in the list command to customize these plots. Below are some example graphs (y axis has been removed for privacy).

```Bash
# Income per mont (in my case, the payroll)
ngtonic month-plot -i
```
<img src="examples/payroll.png" width="600">

```Bash
# Expenses on ocio category per month
ngtonic month-plot -c ocio
```
<img src="examples/ocio.png" width="600">

```Bash
# The month-plot without any options is a good way to know your saving capacity
ngtonic month-plot
```
<img src="examples/month-plot.png" width="600">

```Bash
# And the balance plot will give you a more detailed way to check your cash flow
ngtonic balance-plot
```
<img src="examples/full_balance.png" width="600">

## Instructions to export from supported sources

### ING
Go to the movements view of your account and download the excel format

### Revolut
On the web version, extract and choose excel format. Don't be surprised when you find that the file is, in fact, a CSV.

### Paypal
Go to activity, download, Completed payments. Choose CSV as the output format. PayPal movements are not directly imported, they are used to enrich the information.

## ⚙️ Configuration

### Excluding Movements

Sometimes you may want to exclude certain transactions from your analysis, such as:

 - Transfers between your own accounts or to other banks
 - Large one-time transactions that skew your graphs
 - Any movements you don't want to include in your financial overview

You can exclude these movements using the configuration file located at `.ngtonic/config.yaml`. This file contains a list of filters; any movement matching these filters will be excluded from all commands.

Example configuration:

```yaml
excluded_movements:
  - category: "Inversión"
  - subcategory: "Ingresos de otras entidades"
  - description: "Traspaso emitido Cuenta Nómina"
  - description: "steam"
    value: -675 # Excludes only this specific Steam transaction
```

## 🛠️ Development

```bash
pdm install
$(pdm venv activate)
pre-commit install
```

This command will create a virtual environment, install all dependencies (including Ngtonic itself), and set up helpful commit hooks. Any changes made to the code will take effect immediately without requiring reinstallation.

You can also run manually the linter with `pdm lint` or the formatter with `pdm format`.

## 📦 Releases

The python packages are uploaded from the CI when creating a release, but you can create an whl locally with `pdm build`.
