# Pași pentru a crea repository nou pe GitHub

## 1. Creează repository-ul pe GitHub

1. Mergi pe: https://github.com/new
2. Completează:
   - **Repository name:** `olx-notifications` (sau alt nume)
   - **Description:** "OLX notifications via Telegram"
   - **Visibility:** Private sau Public (la alegere)
   - **NU bifa:** "Add a README file", "Add .gitignore", "Choose a license"
3. Click **"Create repository"**

## 2. Copiază URL-ul repository-ului

După ce creezi repository-ul, GitHub îți va arăta un URL de genul:
`https://github.com/TU_USERNAME/olx-notifications.git`

Copiază acest URL.

## 3. Actualizează remote-ul în terminal

Rulează în terminal (înlocuiește cu URL-ul tău real):
```powershell
git remote set-url origin https://github.com/TU_USERNAME/olx-notifications.git
git push -u origin main
```

## 4. Configurează Secrets pe GitHub

1. Mergi în repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Adaugă:
   - **Name:** `TELEGRAM_BOT_TOKEN`
   - **Value:** `8163333919:AAHi7Zs-OrNlUX_sisTIQBmIQ6MZVcsYDUM`
4. Click **"Add secret"**
5. Repetă pentru:
   - **Name:** `TELEGRAM_CHAT_ID`
   - **Value:** `679733568`

## 5. Activează GitHub Actions

1. Mergi în tab-ul **Actions** din repository
2. Click **"I understand my workflows, enable them"**

Gata! Aplicația va rula automat la fiecare 30 de minute! 🚀

