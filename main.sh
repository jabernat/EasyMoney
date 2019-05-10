#!/usr/bin/env bash
# Starts the EasyMoney application on Linux.

if [ -x "$(command -v mypy)" ]; then
	echo "Type Checking:"
	mypy "main.py"
	echo
fi

echo "Executing:"
python3 "main.py"
