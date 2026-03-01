@echo off
REM Phase 2: Pedagogical Evaluation Runner for Windows
REM ===============================================

echo.
echo 🎓 PHASE 2: PEDAGOGICAL EVALUATION
echo ========================================
echo.
echo This will run LLM-as-judge evaluation + manual review framework
echo for quiz and flashcard quality assessment.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python and add it to PATH.
    pause
    exit /b 1
)

REM Check if virtual environment exists and activate
if exist "..\..\venv\Scripts\activate.bat" (
    echo ⚙️ Activating virtual environment...
    call ..\..\venv\Scripts\activate.bat
) else if exist "..\..\..\venv\Scripts\activate.bat" (
    echo ⚙️ Activating virtual environment from parent directory...
    call ..\..\..\venv\Scripts\activate.bat
) else (
    echo ⚠️ No virtual environment found. Using system Python.
)

REM Check for required files
if not exist "pedagogical_evaluation.py" (
    echo ❌ Required file missing: pedagogical_evaluation.py
    pause
    exit /b 1
)

if not exist "run_phase2_evaluation.py" (
    echo ❌ Required file missing: run_phase2_evaluation.py
    pause
    exit /b 1
)

echo ✅ All required files found.
echo.

REM Show evaluation options
echo 📋 Evaluation Options:
echo    1. Full Evaluation (20 quizzes + 10 flashcard sets + manual review)
echo    2. Quick Test (2 quizzes + 2 flashcard sets)
echo    3. Custom Configuration
echo.

set /p choice="Select option (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Running Full Pedagogical Evaluation...
    echo.
    python run_phase2_evaluation.py
) else if "%choice%"=="2" (
    echo.
    echo 🧪 Running Quick Test...
    echo.
    python run_phase2_evaluation.py test
) else if "%choice%"=="3" (
    echo.
    echo ⚙️ Running Custom Configuration...
    echo.
    python run_phase2_evaluation.py
) else (
    echo.
    echo ❌ Invalid choice. Exiting.
    pause
    exit /b 1
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Evaluation failed!
    echo Check the error messages above for troubleshooting.
) else (
    echo.
    echo 🎉 Evaluation completed successfully!
    echo.
    echo 📁 Results Location:
    echo    • ../../evaluation_results/phase2/ folder
    echo    • Manual review templates ready for scoring
    echo    • LLM judge evaluations complete
    echo.
    echo 📝 Next Steps:
    echo    1. Review LLM evaluation results
    echo    2. Complete manual scoring using templates
    echo    3. Analyze results for research insights
)

echo.
echo Press any key to close...
pause >nul