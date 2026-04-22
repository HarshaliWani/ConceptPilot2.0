# Verify narration_script data quality in MongoDB
# PowerShell script for easy execution

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Narration Script Verification Tool" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run from the backend directory where .venv is located" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Run verification script
Write-Host "Running verification..." -ForegroundColor Green
Write-Host ""

python verify_narration_script.py @args

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Verification complete. Check the output above for results." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
