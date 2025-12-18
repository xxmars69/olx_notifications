# Ghid de Deployment - OLX Notifications

Acest ghid explică cum să rulezi aplicația în cloud, fără să depindă de PC-ul tău.

## Opțiunea 1: GitHub Actions (Recomandat - GRATUIT)

GitHub Actions poate rula aplicația automat la intervale regulate.

### Pași:

1. **Creează un repository pe GitHub:**
   - Mergi pe https://github.com/new
   - Creează un repository nou (ex: `olx-notifications`)
   - Nu adăuga README, .gitignore sau licență (le avem deja)

2. **Încarcă codul:**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USERNAME/olx-notifications.git
   git push -u origin main
   ```

3. **Configurează variabilele de mediu (Secrets):**
   - Mergi în repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Adaugă:
     - `TELEGRAM_BOT_TOKEN` = `8163333919:AAHi7Zs-OrNlUX_sisTIQBmIQ6MZVcsYDUM`
     - `TELEGRAM_CHAT_ID` = `679733568`

4. **Activează Actions:**
   - Mergi în repository → Actions
   - Click "I understand my workflows, enable them"
   - Workflow-ul va rula automat la fiecare 30 de minute

### Limitări GitHub Actions:
- Planul gratuit: max 2000 minute/lună
- Workflow-urile pot rula max 6 ore continuu
- Pentru rulare la fiecare 30 min = ~1440 minute/lună (OK pentru planul gratuit)

---

## Opțiunea 2: Render.com (Alternativă - GRATUIT cu limitări)

Render.com oferă cron jobs gratuite.

### Pași:

1. **Creează cont pe Render.com:**
   - Mergi pe https://render.com
   - Sign up cu GitHub

2. **Creează un Cron Job:**
   - Dashboard → New → Cron Job
   - Connect repository-ul tău de GitHub
   - Settings:
     - **Name:** olx-scraper
     - **Schedule:** `*/30 * * * *` (la fiecare 30 min)
     - **Command:** `python main.py`
     - **Build Command:** `pip install -r requirements.txt`

3. **Configurează Environment Variables:**
   - În settings-ul cron job-ului, adaugă:
     - `TELEGRAM_BOT_TOKEN` = `secret`
     - `TELEGRAM_CHAT_ID` = `679733568`

4. **Deploy:**
   - Click "Create Cron Job"
   - Render va rula automat aplicația conform programului

### Limitări Render.com:
- Planul gratuit: 750 ore/lună
- Cron jobs gratuite rulează la fiecare execuție

---

## Opțiunea 3: Railway.app (Alternativă)

Railway oferă și cron jobs.

### Pași:

1. **Creează cont pe Railway:**
   - Mergi pe https://railway.app
   - Sign up cu GitHub

2. **Creează un proiect nou:**
   - New Project → Deploy from GitHub repo
   - Selectează repository-ul tău

3. **Configurează:**
   - Adaugă variabilele de mediu în Settings → Variables
   - Setează start command: `python main.py`

4. **Pentru cron job:**
   - Railway nu are cron jobs native, dar poți folosi un worker care rulează continuu
   - Sau folosește GitHub Actions + Railway pentru hosting

---

## Recomandare

**Folosește GitHub Actions** pentru că:
- ✅ Complet gratuit pentru planul de bază
- ✅ Ușor de configurat
- ✅ Rulează automat când faci push
- ✅ Nu necesită card de credit
- ✅ Suportă cron jobs

---

## Testare

După deployment, poți testa manual:
- **GitHub Actions:** Mergi în Actions → Selectează workflow-ul → "Run workflow"
- **Render:** Cron job-ul rulează automat conform programului

---

## Actualizare cod

Când faci modificări:
```powershell
git add .
git commit -m "Update"
git push
```

GitHub Actions/Render vor rula automat cu noul cod.

