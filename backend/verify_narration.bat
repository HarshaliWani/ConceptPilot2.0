@echo off
REM Verify narration_script data quality in MongoDB
REM Windows batch script for easy execution

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo  Narration Script Verification Tool
echo ================================================================
echo.

REM Check if venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please run from the backend directory where .venv is located
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run verification script
echo Running verification...
echo.

python verify_narration_script.py %*

REM Keep window open to see results
pause
