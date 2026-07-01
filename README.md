# AI-Powered Job Scraping Dashboard

An automated job scraping dashboard that intelligently collects job postings from Adzuna, Jooble, The Muse, LinkedIn, and Glassdoor. It features an AI-driven Query Expansion service to maximize job coverage, filters the jobs using AI for quality and relevance, and displays results in a modern dashboard. Built with React + Supabase + GitHub Actions/FastAPI.

## Architecture

```
┌──────────────┐     reads/writes      ┌──────────────┐
│   Vercel     │◄──────────────────────►│   Supabase   │
│  (Frontend)  │  Supabase JS SDK       │  (Database)  │
└──────────────┘                        └──────┬───────┘
                                                ▲ writes
                                          ┌─────┴───────┐
                                          │  Scraper    │
                                          │ (Backend)   │
                                          └──────────────┘
```

- **Frontend** — React + Vite + Tailwind CSS + shadcn/ui, deployed on Vercel
- **Database** — Supabase (PostgreSQL), frontend talks directly via the JS SDK
- **Backend / Scraper** — Python + FastAPI + Playwright. Manages robust scheduling, smart AI Query Expansion caching, and a cascading fallback chain across 5 job API providers.
- **AI Filtering & Expansion** — OpenRouter evaluates job descriptions for relevance and dynamically expands search keywords (e.g. `Backend Dev` -> `API Engineer`) to surface hidden jobs.

## Features

- **Cascading Fallback Chain**: Scrapes Adzuna, Jooble, The Muse, LinkedIn, and Glassdoor in sequence, stopping early to optimize API costs if quota is met.
- **AI Query Expansion**: Automatically generates industry-standard synonyms for your keywords to expand search reach, caching them in the database to save tokens.
- **Smart Data Normalization**: Cleans out HTML, deduplicates jobs across multiple API providers, and standardizes employment types/locations.
- **Automated AI Filtering**: Evaluates raw job descriptions to score them out of 100, assigns a category, and auto-trashes irrelevant results before they hit your database.
- **Full Test Suite**: Fully automated `pytest` suite simulating all APIs and databases for rapid, confident iteration.

## Prerequisites

1. **Supabase Project** — URL and keys for frontend (anon) and backend (service role)
2. **OpenRouter API Key** — Required for AI Filtering & Query Expansion
3. **Provider APIs (Optional but recommended)** — Adzuna App ID/Key, Jooble API Key, The Muse API Key.

## Setup

### 1. Supabase Tables

The following tables are utilized in your Supabase project:

- **`jobs`** — Scraped job listings
- **`logs`** — Scraping run logs
- **`keywords`** — Search keywords with enabled/disabled state
- **`settings`** — App configuration
- **`scraper_runs`** — Tracks scraper health and status
- **`search_query_expansions`** — AI generated keywords cache

Run the SQL migration in the Supabase SQL Editor to create missing tables:
```sql
-- See backend/scripts/migration_create_tables.sql
```

### 2. Backend / Scraper (Local or Server Deployment)

The Python backend manages the complex scraper execution. 

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and fill in your keys:
```env
SUPABASE_URL=your_url
SUPABASE_KEY=your_service_role_key
OPENROUTER_API_KEY=your_key
ADZUNA_APP_ID=your_id
ADZUNA_APP_KEY=your_key
JOOBLE_API_KEY=your_key
MUSE_API_KEY=your_key
PORT=8000
```

Start the application:
```bash
python -m backend.app
```

**Running Tests:**
We use `pytest` for rigorous coverage of deduplication, data normalizers, and orchestrator fallbacks.
```bash
PYTHONPATH=. pytest tests/ -v
```

### 3. Frontend Deployment (Vercel)

1. Push the repo to GitHub.
2. In Vercel: Add New Project → Import your GitHub repo.
3. Vercel auto-detects the Vite config from `vercel.json`.
4. Add these **Environment Variables** in Vercel project Settings:

| Variable | Description |
|----------|-------------|
| `VITE_SUPABASE_URL` | Your Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anon/publishable key |

5. Deploy — the frontend talks directly to Supabase.

## Project Structure

```
├── frontend/               # React + Vite dashboard
│   ├── src/
│   │   ├── pages/          # Dashboard, Jobs, Keywords, Logs, Health, Settings
│   │   ├── components/     # Reusable UI components
│   │   ├── lib/            # Supabase client, utilities
│   │   └── contexts/       # Theme providers
│   └── .env.example        # Environment variable template
├── backend/
│   ├── apis/               # Adzuna, Jooble, Muse, LinkedIn, Glassdoor scraper modules
│   ├── services/           # Orchestrator, AI Query Expansion, AI Manager, Normalizer, Deduplicator
│   ├── tests/              # Pytest automated test suite
│   ├── scripts/            # Migration SQL, setup utilities
│   └── requirements.txt
├── .github/workflows/      # GitHub Actions scraper workflow (Optional)
├── vercel.json             # Vercel deployment config (frontend only)
└── README.md
```

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend:** Python, FastAPI, Pytest, Playwright
- **Database:** Supabase (PostgreSQL)
- **AI:** OpenRouter API
- **Deployment:** Vercel (frontend), GitHub Actions / Local (backend)
