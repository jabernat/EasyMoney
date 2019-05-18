# EasyMoney

A stock market simulator for testing and evaluating automated trading
algorithms. A separate [Software Architecture](
https://bitbucket.org/csusm-easymoney/software-architecture/) repository
visualizes dependency relationships.

This was an assignment for CSU San Marcos' CS 441 Software Engineering course.
Tyler Gerritsen, Erik Anderson, and James Abernathy contributed, under the
instruction of Dr. Yongjie Zheng.

Source code is formatted according to the [PEP 8 Style Guide for Python Code](
https://www.python.org/dev/peps/pep-0008/ ). Comment docstrings are formatted
according to the [PEP 257 Docstring Conventions](
https://www.python.org/dev/peps/pep-0257/ ), and use reStructuredText markup
for rich formatting according to [PEP 287 reStructuredText Docstring Format](
https://www.python.org/dev/peps/pep-0287/ ).


## Screenshots
*   The Traders tab controls which trading algorithms will participate in the
    simulation:
    ![EasyMoney's Traders tab with a table listing participating traders](
        ./Pictures/WindowView%20Traders%20Tab.png)

*   The Symbols tab controls which stock symbol data will be available for
    traders to buy and sell during the simulation:
    ![EasyMoney's Symbols tab with a table listing imported stock symbols](
        ./Pictures/WindowView%20Symbols%20Tab.png)

*   The Simulation tab can start, stop, and reset the simulation:
    ![EasyMoney's Simulation tab with buttons to control the simulation](
        ./Pictures/WindowView%20Simulation%20Tab.png)

*   The Statistics tab provides access to trader statistics during and after
    simulations, as well as the ability to save result files:
    ![EasyMoney's Statistics tab displaying a trader's simulated performance](
        ./Pictures/WindowView%20Statistics%20Tab.png)


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
