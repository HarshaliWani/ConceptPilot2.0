@echo off
REM Migrate narration_script field in MongoDB
REM Windows batch script for easy execution

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo  Narration Script Migration Tool
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

REM Check if --apply flag is provided
echo.
echo Migration Tool Options:
echo   - WITHOUT --apply: Preview changes (dry run)
echo   - WITH --apply: Apply changes to database
echo.

if "%1"=="" (
    echo No arguments provided. Running in DRY RUN mode.
    echo To apply changes, use: migrate_narration.bat --apply
    echo.
    python migrate_narration_script.py
) else (
    python migrate_narration_script.py %*
)

echo.
echo ================================================================
echo Migration complete. Check the output above for results.
echo ================================================================
echo.

REM Keep window open to see results
pause
