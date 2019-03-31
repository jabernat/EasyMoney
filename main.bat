@ECHO OFF
:: Starts the EasyMoney application on Windows.

python "main.py"

IF ERRORLEVEL 1 (
	PAUSE
)
