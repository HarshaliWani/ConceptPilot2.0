# Migrate narration_script field in MongoDB
# PowerShell script for easy execution

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Narration Script Migration Tool" -ForegroundColor Cyan
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

# Check if --apply flag is provided
Write-Host ""
Write-Host "Migration Tool Options:" -ForegroundColor Yellow
Write-Host "  - WITHOUT --apply: Preview changes (dry run)" -ForegroundColor Yellow
Write-Host "  - WITH --apply: Apply changes to database" -ForegroundColor Yellow
Write-Host ""

if ($args.Count -eq 0) {
    Write-Host "No arguments provided. Running in DRY RUN mode." -ForegroundColor Yellow
    Write-Host "To apply changes, use: .\migrate_narration.ps1 --apply" -ForegroundColor Yellow
    Write-Host ""
    python migrate_narration_script.py
} else {
    python migrate_narration_script.py @args
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Migration complete. Check the output above for results." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
