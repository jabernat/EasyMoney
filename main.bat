@SETLOCAL
@ECHO OFF
:: Starts the EasyMoney application on Windows.

ECHO Type Checking:
mypy "main.py"
SET _ERRORLEVEL_PYPY=%ERRORLEVEL%
ECHO.

ECHO Executing:
python "main.py"
SET /A _ERRORLEVEL_COMBINED=%_ERRORLEVEL_PYPY% + %ERRORLEVEL%

:: Pause before closing the console window if an error occured.
IF %_ERRORLEVEL_COMBINED% NEQ 0 (
	ECHO.
	PAUSE
)
