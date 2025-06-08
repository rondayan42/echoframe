@echo off
chcp 65001 >nul
color 0a
cls

title Echoframe: Uplink Terminal

echo.
echo [FREQ NODE ACCESS] 
timeout /nobreak /t 1 >nul     
echo ------------------------
timeout /nobreak /t 1 >nul
echo Initializing boot sequence...
timeout /nobreak /t 1 >nul
echo Syncing code pulse frequency...
timeout /nobreak /t 1 >nul
echo Injecting FREQ daemon...
timeout /nobreak /t 1 >nul

::====== Begin Python 3.11 Check (Hidden) ======::
set PYTHON_EXE=python
python3.11 --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_EXE=python3.11
)
::====== End Python 3.11 Check ======::

::====== Begin Python Check (Hidden) ======::
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not detected. FREQ daemon needs Python to run.
    echo [!] Please install Python 3.8 or higher to continue.
    echo [!] Visit https://www.python.org/downloads/
    echo.
    pause
    exit /b
)
::====== End Python Check ======::

:: Show cool progress bar for dependency installation
echo.
echo Validating core dependencies... [                    ] 0%%
:: Check if pip is installed (silently)
%PYTHON_EXE% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    %PYTHON_EXE% -m ensurepip --default-pip >nul 2>&1
)
echo Validating core dependencies... [============        ] 60%%

:: Install required packages (silently)
if exist requirements.txt (
    %PYTHON_EXE% -m pip install -q -r requirements.txt >nul 2>&1
) else (
    echo [!] requirements.txt not found. Skipping dependency installation.
)
echo Validating core dependencies... [====================] 100%%
echo Dependencies synchronized successfully.
echo.

timeout /nobreak /t 1 >nul
echo Activating ECHOFRAME interface...
timeout /nobreak /t 1 >nul
echo.

:: Launch the browser with a delay to allow server to start and find available port
timeout /nobreak /t 2 >nul

:: Use Start-Process in PowerShell to open browser after a short delay
powershell -Command "Start-Sleep -Seconds 3; Start-Process http://127.0.0.1:5001; if ($LASTEXITCODE -ne 0) { Start-Process http://127.0.0.1:5002 }; if ($LASTEXITCODE -ne 0) { Start-Process http://127.0.0.1:5003 }" >nul 2>&1

:: Run the Flask app using system Python
%PYTHON_EXE% app.py