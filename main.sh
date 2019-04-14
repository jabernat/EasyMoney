#!/usr/bin/env bash
# Starts the EasyMoney application on Linux.

echo "Type Checking:"
mypy "main.py"
echo

echo "Executing:"
python3 "main.py"
