# AI-Powered Job Scraping Dashboard

Automated job scraping dashboard that collects jobs from LinkedIn, Greenhouse,
Lever, and Ashby, filters them using AI, and displays results in a modern
dashboard. Built with React + Supabase + GitHub Actions.

## Architecture

```
┌──────────────┐     reads/writes      ┌──────────────┐
│   Vercel     │◄──────────────────────►│   Supabase   │
│  (Frontend)  │  Supabase JS SDK       │  (Database)  │
└──────────────┘                        └──────┬───────┘
                                                ▲ writes
                                          ┌─────┴───────┐
                                          │GitHub Actions│
                                          │  (Scraper)   │
                                          └──────────────┘
```

- **Frontend** — React + Vite + Tailwind CSS + shadcn/ui, deployed on Vercel
- **Database** — Supabase (PostgreSQL), frontend talks directly via the JS SDK
- **Scraper** — Python + Playwright, runs daily in GitHub Actions, writes to Supabase
- **AI Filtering** — OpenRouter (free model) evaluates job descriptions

## Features

- Automated scraping from LinkedIn, Greenhouse, Lever, Ashby
- AI-powered job filtering with customizable prompt
- Keyword management (CRUD)
- Job review dashboard with search, sort, filter, CSV export
- Daily scheduled scraping via GitHub Actions (configurable in YAML)
- Manual scraper trigger from GitHub Actions dashboard
- System health monitoring

## Prerequisites

1. **Supabase Project** — URL and anon key for the frontend, service role key for the scraper
2. **OpenRouter API Key** — Free tier works (`gpt-oss-20b:free`)
3. **GitHub Account** — For the scraper runner
4. **Vercel Account** — For frontend hosting

## Setup

### 1. Supabase Tables

The following tables need to exist in your Supabase project:

- **`jobs`** — scraped job listings (already exists if you migrated from the old setup)
- **`logs`** — scraping run logs (already exists)
- **`keywords`** — search keywords with enabled/disabled state (already exists)
- **`settings`** — app configuration (single row)
- **`scraper_runs`** — tracks scraper health and status

Run the SQL migration in Supabase SQL Editor to create missing tables:
```
backend/scripts/migration_create_tables.sql
```

### 2. GitHub Secrets

These are required by the GitHub Actions scraper workflow. Add them in:
**GitHub repo → Settings → Secrets and variables → Actions**

| Secret | Description |
|--------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase service role key (not anon key) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key |

### 3. Frontend Deployment (Vercel)

1. Push the repo to GitHub
2. In Vercel: Add New Project → Import your GitHub repo
3. Vercel auto-detects the Vite config from `vercel.json`
4. Add these **Environment Variables** in Vercel project Settings:

| Variable | Description |
|----------|-------------|
| `VITE_SUPABASE_URL` | Your Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anon/publishable key |
| `VITE_GITHUB_REPO` | `https://github.com/your-username/your-repo` |

5. Deploy — the frontend talks directly to Supabase, no backend server needed

### 4. Local Development

```bash
# Frontend
cd frontend
cp .env.example .env
# Fill in your Supabase URL and anon key
npm install
npm run dev

# Scraper (runs locally)
cd backend
pip install -r requirements.txt
playwright install chromium
python -c "import asyncio; from backend.services.orchestrator import orchestrator; asyncio.run(orchestrator.run_all())"
```

## Running the Scraper

### Daily (automatic)
The scraper runs daily at 8 AM via the GitHub Actions workflow:
`.github/workflows/scrape.yml`

### Manual
Go to GitHub → Actions → **Daily Job Scraper** → **Run workflow**

## Project Structure

```
├── frontend/               # React + Vite dashboard
│   ├── src/
│   │   ├── pages/          # Dashboard, Jobs, Keywords, Logs, Health, Settings
│   │   ├── components/     # Reusable UI components
│   │   ├── lib/            # Supabase client, utilities
│   │   └── contexts/       # Theme, Toast providers
│   └── .env.example        # Environment variable template
├── backend/
│   ├── scrapers/           # LinkedIn, Lever, Greenhouse, Ashby scrapers
│   ├── services/           # Orchestrator, AI, DB, extractors, normalizers
│   ├── routers/            # API endpoints (legacy)
│   ├── scripts/            # Migration SQL, setup utilities
│   └── requirements.txt
├── .github/workflows/      # GitHub Actions scraper workflow
├── vercel.json             # Vercel deployment config (frontend only)
└── README.md
```

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts
- **Database:** Supabase (PostgreSQL)
- **State:** TanStack React Query
- **Scraping:** Playwright, BeautifulSoup
- **AI:** OpenRouter API (gpt-oss-20b:free)
- **CI/CD:** GitHub Actions (scraper), Vercel (frontend)
