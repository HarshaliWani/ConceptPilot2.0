# Research Evaluation Runner (PowerShell)
# =====================================
# Enhanced Windows runner with proper error handling

param(
    [switch]$Mini,
    [int]$Count = 5,
    [string]$Topic = "Quadratic Equations"
)

Write-Host ""
Write-Host "🔬 LESSON GENERATION RESEARCH EVALUATION" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Check Python installation
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python not found! Please install Python and add it to PATH." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    
    # Check and activate virtual environment if available
    if (Test-Path "..\..\venv\Scripts\Activate.ps1") {
        Write-Host "⚙️  Activating virtual environment..." -ForegroundColor Yellow
        & "..\..\venv\Scripts\Activate.ps1"
    } elseif (Test-Path "..\..\venv\Scripts\activate.bat") {
        Write-Host "⚙️  Activating virtual environment (batch)..." -ForegroundColor Yellow
        cmd /c "..\..\venv\Scripts\activate.bat && powershell"
    } else {
        Write-Host "⚠️  No virtual environment found. Using system Python." -ForegroundColor Yellow
    }
    
    # Check if required files exist
    $requiredFiles = @("evaluation_framework.py", "run_evaluation.py", "validate_lessons.py")
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-Host "❌ Required file missing: $file" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✅ All required files found." -ForegroundColor Green
    Write-Host ""
    
    # Determine what to run based on parameters
    if ($Mini) {
        Write-Host "🧪 Running Mini-Evaluation ($Count lessons)" -ForegroundColor Cyan
        Write-Host "This is a quick test to validate the system." -ForegroundColor Gray
        Write-Host ""
        
        $process = Start-Process -FilePath "python" -ArgumentList "validate_lessons.py", "mini", $Count -NoNewWindow -Wait -PassThru
        
    } else {
        Write-Host "🚀 Running Full Research Evaluation (100 lessons)" -ForegroundColor Cyan
        Write-Host "This will take several minutes to complete." -ForegroundColor Gray
        Write-Host ""
        
        # Confirm execution for full evaluation
        $confirm = Read-Host "Continue with full evaluation? (y/N)"
        if ($confirm -notin @('y', 'Y', 'yes', 'YES')) {
            Write-Host "Evaluation cancelled." -ForegroundColor Yellow
            exit 0
        }
        
        Write-Host ""
        Write-Host "⏳ Starting full evaluation..." -ForegroundColor Green
        
        $process = Start-Process -FilePath "python" -ArgumentList "run_evaluation.py" -NoNewWindow -Wait -PassThru
    }
    
    # Check exit code
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "🎉 Evaluation completed successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Show results directory
        if (Test-Path "evaluation_results") {
            $resultFiles = Get-ChildItem "evaluation_results" | Sort-Object LastWriteTime -Descending
            if ($resultFiles.Count -gt 0) {
                Write-Host "📁 Latest results:" -ForegroundColor Cyan
                $resultFiles | Select-Object -First 3 | ForEach-Object {
                    Write-Host "   📄 $($_.Name)" -ForegroundColor Gray
                }
            }
        }
        
    } else {
        Write-Host ""
        Write-Host "❌ Evaluation failed (Exit code: $($process.ExitCode))" -ForegroundColor Red
        Write-Host "Check the error messages above for troubleshooting." -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "   • Ensure Python is installed and in PATH" -ForegroundColor Gray
    Write-Host "   • Check that all dependencies are installed" -ForegroundColor Gray
    Write-Host "   • Try running a mini evaluation first: -Mini" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")