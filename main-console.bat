@SETLOCAL
@ECHO OFF
:: Starts the EasyMoney application on Windows with a visible event-log console.

:: Perform static analysis type-checking if available.
where mypy > NUL
IF NOT ERRORLEVEL 1 (
	:: Mypy is installed.
	ECHO Type Checking:
	mypy "main.py"
	ECHO.
)

ECHO Executing:
python "main.py"

:: Pause before closing the console window.
ECHO.
PAUSE
