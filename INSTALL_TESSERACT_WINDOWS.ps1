# ⚡ ElectroVision AI - Tesseract OCR Installer for Windows
# This script automatically installs Tesseract OCR for enhanced PDF text extraction

Write-Host "🔧 ElectroVision AI - Tesseract OCR Installer" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if Tesseract is already installed
try {
    $version = tesseract --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tesseract is already installed!" -ForegroundColor Green
        Write-Host "$version"
        exit 0
    }
} catch {
    Write-Host "❌ Tesseract not found in PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Installing Tesseract OCR for enhanced PDF processing..." -ForegroundColor Yellow

# Method 1: Try Chocolatey (fastest)
Write-Host ""
Write-Host "📦 Trying installation via Chocolatey..." -ForegroundColor Blue

try {
    $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoInstalled) {
        Write-Host "✅ Chocolatey found - installing Tesseract..." -ForegroundColor Green
        choco install tesseract -y
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Tesseract installed successfully via Chocolatey!" -ForegroundColor Green
            Write-Host "🔄 Please restart your terminal and try uploading again." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "⚠️ Chocolatey not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Chocolatey installation failed" -ForegroundColor Red
}

# Method 2: Try Scoop
Write-Host ""
Write-Host "📦 Trying installation via Scoop..." -ForegroundColor Blue

try {
    $scoopInstalled = Get-Command scoop -ErrorAction SilentlyContinue
    if ($scoopInstalled) {
        Write-Host "✅ Scoop found - installing Tesseract..." -ForegroundColor Green
        scoop install tesseract
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Tesseract installed successfully via Scoop!" -ForegroundColor Green
            Write-Host "🔄 Please restart your terminal and try uploading again." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "⚠️ Scoop not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Scoop installation failed" -ForegroundColor Red
}

# Method 3: Download and install manually
Write-Host ""
Write-Host "📥 Attempting manual download and installation..." -ForegroundColor Blue

try {
    $downloadUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    $installerPath = "$env:TEMP\tesseract-installer.exe"
    
    Write-Host "⬇️ Downloading Tesseract installer..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    
    Write-Host "🚀 Running installer (silent mode)..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
    
    # Add to PATH
    $tesseractPath = "C:\Program Files\Tesseract-OCR"
    if (Test-Path $tesseractPath) {
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($currentPath -notlike "*$tesseractPath*") {
            Write-Host "🔧 Adding Tesseract to system PATH..." -ForegroundColor Yellow
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$tesseractPath", "Machine")
        }
        
        Write-Host "✅ Tesseract installed successfully!" -ForegroundColor Green
        Write-Host "🔄 Please restart your terminal and backend server, then try uploading again." -ForegroundColor Yellow
        
        # Clean up
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        exit 0
    }
} catch {
    Write-Host "❌ Manual installation failed: $_" -ForegroundColor Red
}

# If all methods failed
Write-Host ""
Write-Host "❌ Automatic installation failed. Please install manually:" -ForegroundColor Red
Write-Host ""
Write-Host "📋 Manual Installation Steps:" -ForegroundColor Yellow
Write-Host "1. Download: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
Write-Host "2. Run the installer: tesseract-ocr-w64-setup-5.x.x.exe" -ForegroundColor White
Write-Host "3. Add to PATH: C:\Program Files\Tesseract-OCR" -ForegroundColor White
Write-Host "4. Restart terminal and backend server" -ForegroundColor White
Write-Host ""
Write-Host "💡 ElectroVision AI will work without OCR, but with limited text extraction from scanned PDFs." -ForegroundColor Cyan

exit 1 