# RAG Explorer - Windows Setup Script
# Run this script to automatically set up the environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG Explorer - Automated Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$backendPath = ".\backend"
$frontendPath = ".\frontend"

# Check Python
Write-Host "`n[1/6] Checking Python installation..." -ForegroundColor Yellow
$pythonPath = "C:\Python314\python.exe"
if (Test-Path $pythonPath) {
    & $pythonPath --version
} else {
    Write-Host "ERROR: Python not found at $pythonPath! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "`n[2/6] Checking Node.js installation..." -ForegroundColor Yellow
node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found! Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "`n[3/6] Setting up Python environment..." -ForegroundColor Yellow
cd $backendPath
if (!(Test-Path "venv")) {
    & $pythonPath -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate venv and install requirements
& ".\venv\Scripts\activate.ps1"
Write-Host "Virtual environment activated" -ForegroundColor Green

Write-Host "`n[4/6] Installing Python dependencies..." -ForegroundColor Yellow
& $pythonPath -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python packages" -ForegroundColor Red
    exit 1
}
Write-Host "Python dependencies installed" -ForegroundColor Green

# Check for .env file
if (!(Test-Path ".env")) {
    Write-Host "`n[!] .env file not found!" -ForegroundColor Red
    Write-Host "    Creating .env.example template..." -ForegroundColor Yellow
    Write-Host "    Please edit it with your Groq API key!" -ForegroundColor Yellow
    copy ".env.example" ".env"
}

# Setup Frontend
cd ..\$frontendPath
Write-Host "`n[5/6] Installing Node dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Node packages" -ForegroundColor Red
    exit 1
}
Write-Host "Node dependencies installed" -ForegroundColor Green

Write-Host "`n[6/6] Setup complete!" -ForegroundColor Green
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend\.env with your Groq API key" -ForegroundColor White
Write-Host "2. In Terminal 1: cd backend && venv\Scripts\activate && python app.py" -ForegroundColor White
Write-Host "3. In Terminal 2: cd frontend && npm start" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
