# Run from the project root (the folder containing manage.py)
$ErrorActionPreference = "Stop"

$required = @(
  "manage.py", "requirements.txt", ".gitignore", "README.md",
  "volunteerconnect\settings.py", "volunteerconnect\urls.py",
  "volunteerconnect\wsgi.py", "volunteerconnect\__init__.py",
  "accounts\models.py", "accounts\migrations\0001_initial.py",
  "core\models.py", "core\migrations\0001_initial.py",
  "core\migrations\0002_seed_milestones.py",
  "reports\views.py", "reports\urls.py",
  "templates", "static"
)

$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing) {
  Write-Host "`nMISSING - fix these before pushing:" -ForegroundColor Red
  $missing | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
  exit 1
}
Write-Host "All required files found." -ForegroundColor Green

if (Select-String -Path "volunteerconnect\settings.py" -Pattern "DEBUG\s*=\s*True" -Quiet) {
  Write-Host "Note: DEBUG = True in settings.py (fine for coursework, not for deployment)." -ForegroundColor Yellow
}

if (-not (Test-Path ".git")) { git init }
git add .

$tracked = git diff --cached --name-only
if ($tracked -match "db\.sqlite3|^\.?venv/") {
  Write-Host "db.sqlite3 or venv is staged - check .gitignore." -ForegroundColor Red
  exit 1
}

git commit -m "Initial commit: VolunteerConnect"
git branch -M main

$url = Read-Host "Paste your GitHub repo URL"
git remote remove origin 2>$null
git remote add origin $url
git push -u origin main
Write-Host "Done." -ForegroundColor Green
