@echo off
REM Research Evaluation Runner for Windows
REM ===================================

echo.
echo 🔬 LESSON GENERATION RESEARCH EVALUATION
echo =====================================
echo.
echo This will generate 100 lessons across 20 STEM topics for research analysis.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python and add it to PATH.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "..\..\venv\Scripts\activate.bat" (
    echo ⚙️ Activating virtual environment...
    call ..\..\venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found. Using system Python.
)

REM Run the evaluation
echo 🚀 Starting evaluation...
echo.
python run_evaluation.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Evaluation failed!
    echo Check the error messages above for troubleshooting.
) else (
    echo.
    echo ✅ Evaluation completed successfully!
    echo Check the evaluation_results/ folder for output files.
)

echo.
echo Press any key to close...
pause >nul