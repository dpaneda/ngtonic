#! /usr/bin/env bash

ruff check
ruff_exit=$?

mypy .
mypy_exit=$?

vulture src --min-confidence 70
vulture_exit=$?

ruff format . --diff
format_exit=$?

if [[ $ruff_exit -ne 0 || $mypy_exit -ne 0 || $vulture_exit -ne 0 || $format_exit -ne 0 ]]; then
    echo "There is some linting errors, check below or execute pdm lint locally to get more details"
    exit 1
fi

exit 0
