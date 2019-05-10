# EasyMoney

A stock market simulator for testing and evaluating automated trading algorithms.

This class project was written exclusively by James Abernathy.

Source code is formatted according to the [PEP 8 Style Guide for Python Code](
https://www.python.org/dev/peps/pep-0008/ ). Comment docstrings are formatted
according to the [PEP 257 Docstring Conventions](
https://www.python.org/dev/peps/pep-0257/ ), and use reStructuredText markup
for rich formatting according to [PEP 287 reStructuredText Docstring Format](
https://www.python.org/dev/peps/pep-0287/ ).


## Installation

To install EasyMoney, first clone a working copy or extract the project folder
to your local computer. Next, install all required Python modules by opening
a command prompt such as `cmd.exe` or `bash` in the project folder and running
the following command:
```
pip install -r requirements.txt
```

If you want to use the [Mypy]( http://mypy-lang.org/ ) tool for static analysis
type-checking, install it as well with the following command:
```
pip install mypy
```


## Running EasyMoney

On Windows, double-click `main.vbs` to run without displaying the logging
console, or double-click `main-console.bat` to run EasyMoney with a separate
console-based debug event log. The console version also runs Mypy static
analysis if available.

On Linux, change `main.sh` to executable and then run it with the following
commands:
```
chmod +x main.sh
./main.sh
```
