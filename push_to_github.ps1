# ============================================================
#  Envoi du projet MiniLink sur GitHub (compte : aflesec)
#  Usage : .\push_to_github.ps1
#  Prerequis : depot PUBLIC "minilink-api" deja cree sur GitHub (vide)
# ============================================================

$PSEUDO = "aflesec"
$REPO   = "minilink-api"

git init -b main
git add .
git commit -m "feat: projet MiniLink complet (app, docker, jenkins, terraform, monitoring)"
git remote remove origin 2>$null
git remote add origin "https://github.com/$PSEUDO/$REPO.git"
git push -u origin main

Write-Host ""
Write-Host "Termine. Depot : https://github.com/$PSEUDO/$REPO" -ForegroundColor Green
