@echo off
:: Determine the directory where the batch script is located
set "script_dir=%~dp0"

:: Prompt for OpenAI API key
echo if you do not have an API key visit https://openai.com/blog/openai-api
echo Please enter your OpenAI API key and press Enter:
set /p openai_api_key="OpenAI API Key: "
echo You entered: %openai_api_key%

:: Confirm with the user that this is correct
set /p confirm="Is this correct? (Y/N): "
if /i "%confirm%" neq "Y" (
    echo Restart the script to try again. Exiting.
)

if "%openai_api_key%"=="" (
    echo No OpenAI API key entered. Skipping .env creation.
)

:: Write to .env file
echo OPENAI_API_KEY=%openai_api_key% > "%script_dir%.env"
echo .env file created in the script directory with your OpenAI API key.
pause
:: Try to get Python version
python --version > "%script_dir%tmp_version.txt" 2>&1
set /p pyversion=<"%script_dir%tmp_version.txt"
del "%script_dir%tmp_version.txt"

:: Check if Python is installed
if "%pyversion%"=="" (
    echo Python is not installed. Please install Python and try again.
    goto end
)

echo %pyversion%
set pyversion=%pyversion:Python =%

:: Extract major and minor version
for /f "tokens=1-3 delims=." %%a in ("%pyversion%") do (
    set major=%%a
    set minor=%%b
)

:: Check if version is 3.11.x
if "%major%"=="3" if "%minor%"=="11" (
    echo Installing requirements from requirements.txt...
    python -m pip install -r requirements.txt

    echo Creating shortcut on Desktop...
    powershell -ExecutionPolicy Bypass -File "%script_dir%createShortcut.ps1"

    echo Setup Complete! Open App using shortcut on desktop named "Run Zara"
    pause
) else (
    echo Your Python version is not 3.11.x. (%pyversion%)
    echo Please install Python 3.11.x to continue.
    echo Note: There might be newer versions of Python. If you're having an issue with installing FAISS-cpu, it is only supported in Python 3.11 as per the last update of this application.
)

:end
pause
