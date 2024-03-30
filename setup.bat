@echo off
echo Installing requirements from requirements.txt...
python -m pip install -r requirements.txt

echo Creating shortcut on Desktop...
powershell -ExecutionPolicy Bypass -File createShortcut.ps1

echo Setup Complete!
pause
