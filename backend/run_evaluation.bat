@echo off
REM Main Evaluation Runner - ConceptPilot 2.0
REM =========================================

echo.
echo 🔬 CONCEPTPILOT 2.0 RESEARCH EVALUATION SYSTEM
echo ==============================================
echo.
echo Choose evaluation phase to run:
echo.
echo 1. Phase 1: Technical System Validation (100 lessons, technical metrics)
echo 2. Phase 2: Pedagogical Content Quality (LLM-judge + manual review)  
echo 3. Complete Evaluation (Both phases sequentially)
echo 4. Quick Test (Small sample from each phase)
echo 5. View Results (Open results directory)
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting Phase 1: Technical System Validation...
    echo.
    cd evaluation\phase1
    call run_research_evaluation.bat
    cd ..\..
) else if "%choice%"=="2" (
    echo.
    echo 🎓 Starting Phase 2: Pedagogical Quality Assessment...
    echo.
    cd evaluation\phase2
    call run_phase2_evaluation.bat
    cd ..\..
) else if "%choice%"=="3" (
    echo.
    echo 🔬 Starting Complete Two-Phase Evaluation...
    echo Phase 1: Technical validation first...
    echo.
    cd evaluation\phase1
    call run_research_evaluation.bat
    cd ..\phase2
    echo.
    echo Phase 2: Pedagogical assessment...
    echo.
    call run_phase2_evaluation.bat
    cd ..\..
) else if "%choice%"=="4" (
    echo.
    echo 🧪 Running Quick Test Suite...
    echo.
    echo Testing Phase 1 (5 lessons)...
    cd evaluation\phase1
    python validate_lessons.py mini 5
    cd ..\phase2
    echo.
    echo Testing Phase 2 (2 items)...
    python run_phase2_evaluation.py test
    cd ..\..
) else if "%choice%"=="5" (
    echo.
    echo 📁 Opening Results Directory...
    start "" "evaluation_results"
) else (
    echo.
    echo ❌ Invalid choice. Please run again and select 1-5.
    pause
    exit /b 1
)

echo.
echo ✅ Evaluation completed!
echo.
echo 📊 Results Location:
echo    • evaluation_results\phase1\ - Technical validation results
echo    • evaluation_results\phase2\ - Pedagogical assessment results
echo.
echo 📝 Documentation:
echo    • evaluation\COMPLETE_RESEARCH_EVALUATION_GUIDE.md - Complete guide
echo    • evaluation\phase1\RESEARCH_EVALUATION_README.md - Phase 1 details  
echo    • evaluation\phase2\PHASE2_PEDAGOGICAL_EVALUATION.md - Phase 2 details
echo.

pause