# Deployment Guide

This guide covers publishing the source code to GitHub and deploying the Flask application to Render.

> **Two different links.** The **GitHub repository URL** is where the source code lives. The **Render URL**
> is the running application. They are not the same link. Do not write either URL into the README or
> report until it actually exists.

---

## Part 1 — Prepare the local Git repository

Run these commands in the project root (the folder containing `app.py`).

```powershell
# Initialise the repository
git init -b main

# Set your identity (use your own name and email)
git config user.name "Harshad Babulal Imale"
git config user.email "your-email@example.com"

# Confirm that no secrets are staged
git status
```

Before the first commit, verify the ignore rules work:

```powershell
git check-ignore -v .venv .env __pycache__/ 2>$null
```

`.venv` and `.env` must be ignored. `.env.example` must still be tracked.

```powershell
git add .
git status
git commit -m "Initial commit: Prompt-Based Information Extraction System (MCA practical)"
```

Confirm that no environment file was committed:

```powershell
git ls-files | Select-String -Pattern "\.env$|\.venv|__pycache__|\.pytest_cache"
```

This must print nothing.

---

## Part 2 — Publish to GitHub

You have two options. **Do not invent a repository URL.**

### Option A — GitHub website (no extra tools)

1. Sign in at <https://github.com>.
2. Click **New repository**.
3. Repository name: `prompt-information-extractor`
4. Choose **Public** (or Private) and **do not** add a README or .gitignore (they already exist).
5. Click **Create repository**.
6. Copy the repository URL shown, then run:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/prompt-information-extractor.git
git push -u origin main
```

When prompted, sign in with a **Personal Access Token** (not your account password).

### Option B — GitHub CLI

If you install the GitHub CLI (`winget install --id GitHub.cli` or from <https://cli.github.com>):

```powershell
gh auth login
gh repo create prompt-information-extractor --public --source=. --remote=origin --push
```

After publishing, copy the real repository URL into the README table and into `docs/DEPLOYMENT.md`.

---

## Part 3 — Deploy to Render

### Option A — Blueprint (uses `render.yaml`)

1. Push the repository to GitHub (Part 2).
2. Go to <https://dashboard.render.com> and sign in.
3. Click **New +** → **Blueprint**.
4. Connect your GitHub account and select the `prompt-information-extractor` repository.
5. Render reads `render.yaml`. Review and click **Apply**.
6. Wait for the build to finish. The first free-tier build can take a few minutes.

### Option B — Manual Web Service

If Render does not use the blueprint, create a **New Web Service** and set:

| Setting | Value |
|---|---|
| Environment | Python 3 |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60` |
| Health check path | `/api/health` |
| Environment variables | none required |

`requirements.txt` installs Gunicorn automatically on Render's Linux workers.

---

## Part 4 — Verify the deployment

Replace `YOUR-APP` with the real Render service name.

```powershell
# 1. Health endpoint
Invoke-RestMethod https://YOUR-APP.onrender.com/api/health

# 2. Three test scenarios
Invoke-RestMethod -Method Post https://YOUR-APP.onrender.com/api/tests/run -ContentType "application/json" -Body "{}"

# 3. Extraction over the deployed API
Invoke-RestMethod -Method Post https://YOUR-APP.onrender.com/api/extract `
  -ContentType "application/json" `
  -Body '{"paragraph":"A Python workshop will be held on 5 May 2027 in the Computer Lab.","mode":"standard"}'
```

Then open `https://YOUR-APP.onrender.com` in a browser and run the three checks:

1. The **Extractor** tab loads the sample and returns all five fields.
2. The **Test Suite** tab reports **3 / 3 passed**.
3. The **Schema & Validation** tab detects the invalid example.

Only after these succeed should the live URL be written into the README and report.

---

## Part 5 — Updating the deployment

```powershell
git add .
git commit -m "Describe your change"
git push
```

Render redeploys automatically when `autoDeploy` is enabled.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Build fails on Gunicorn | Windows-only local environment | Render installs Gunicorn from `requirements.txt` automatically; do not remove the sys_platform marker |
| `gunicorn: command not found` locally | Gunicorn is not installed on Windows | Use `py app.py` locally; Gunicorn is for the Linux host only |
| Health check fails | App not listening on `$PORT` | Ensure the start command binds `0.0.0.0:$PORT` |
| 502 from Render | App crashed at startup | Check the Render logs for a Python traceback |
| Blank page | Static files not committed | Confirm `static/vendor/` is tracked by Git |
| First request is slow | Free tier cold start | Wait and retry; the health endpoint warms the app |

---

## Security checklist before pushing

- [ ] `.env` is not tracked (`git ls-files | Select-String "\.env$"` prints nothing).
- [ ] `.venv/` and `__pycache__/` are not tracked.
- [ ] No API keys, tokens, or passwords appear anywhere in the source.
- [ ] `render.yaml` contains no secrets.
- [ ] `.env.example` contains placeholders only.
