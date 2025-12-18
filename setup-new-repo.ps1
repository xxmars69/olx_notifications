# Script pentru a configura noul repository GitHub
# Rulează acest script DUPĂ ce ai creat repository-ul pe GitHub

Write-Host "=== Configurare Repository GitHub ===" -ForegroundColor Cyan
Write-Host ""

# Solicită URL-ul repository-ului
$repoUrl = Read-Host "Introdu URL-ul repository-ului tău (ex: https://github.com/username/olx-notifications.git)"

if ($repoUrl -eq "") {
    Write-Host "Eroare: URL-ul nu poate fi gol!" -ForegroundColor Red
    exit 1
}

# Verifică dacă URL-ul este valid
if (-not ($repoUrl -match "https://github.com/.*\.git$")) {
    Write-Host "Eroare: URL-ul nu pare valid. Format așteptat: https://github.com/username/repo.git" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Actualizare remote URL..." -ForegroundColor Yellow
git remote set-url origin $repoUrl

Write-Host "Verificare remote..." -ForegroundColor Yellow
git remote -v

Write-Host ""
Write-Host "Push către GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCES! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Următorii pași:" -ForegroundColor Cyan
    Write-Host "1. Mergi pe: $repoUrl" -ForegroundColor White
    Write-Host "2. Settings → Secrets and variables → Actions" -ForegroundColor White
    Write-Host "3. Adaugă secrets:" -ForegroundColor White
    Write-Host "   - TELEGRAM_BOT_TOKEN = 8163333919:AAHi7Zs-OrNlUX_sisTIQBmIQ6MZVcsYDUM" -ForegroundColor White
    Write-Host "   - TELEGRAM_CHAT_ID = 679733568" -ForegroundColor White
    Write-Host "4. Activează Actions în tab-ul Actions" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Eroare la push! Verifică că ai creat repository-ul pe GitHub." -ForegroundColor Red
    Write-Host "URL repository: https://github.com/new" -ForegroundColor Yellow
}

