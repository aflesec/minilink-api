#!/usr/bin/env bash
# Envoi du projet MiniLink sur GitHub (compte : aflesec)
set -e

PSEUDO="aflesec"
REPO="minilink-api"

git init -b main
git add .
git commit -m "feat: projet MiniLink complet (app, docker, jenkins, terraform, monitoring)"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$PSEUDO/$REPO.git"
git push -u origin main

echo ""
echo "Termine. Depot : https://github.com/$PSEUDO/$REPO"
