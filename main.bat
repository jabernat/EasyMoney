@SETLOCAL
@ECHO OFF
:: Starts the EasyMoney application on Windows.

ECHO Type Checking:
mypy "main.py"
ECHO.

ECHO Executing:
python "main.py"

:: Pause before closing the console window
ECHO.
PAUSE
