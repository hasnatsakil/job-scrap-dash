# AI-Powered Job Scraping Dashboard

A lightweight, modular, production-ready Job Scraping Dashboard designed to run on Render. This application automates job searching from multiple sources, filters jobs using an AI model via OpenRouter, and stores accepted jobs in Google Sheets. It includes a modern React dashboard to monitor, manage, and review scraped jobs.

## Features

- **Automated Web Scraping:** Uses Playwright to mimic X-Ray searches across job boards (LinkedIn, Greenhouse, Lever, Ashby, etc.).
- **AI Filtering:** Swappable AI provider (default OpenRouter) evaluates job descriptions based on a customizable prompt and issues Keep/Reject decisions.
- **Google Sheets Database:** Uses Google Sheets as a completely stateless persistence layer. No external SQL database needed.
- **Deduplication:** Normalizes data and prevents duplicates by Job URL and Company+Title signatures.
- **Budget Management:** Tracks AI usage to stay within free-tier OpenRouter limits.
- **Dashboard UI:** React (Vite) + Tailwind CSS + shadcn/ui dashboard to review statistics, jobs, system health, and configure the application.

## Prerequisites

1. **Google Service Account Credentials:** Base64-encoded JSON credentials with access to a target Google Sheet.
2. **OpenRouter API Key:** Used to run the `gpt-oss-20b:free` model for filtering jobs.
3. **Docker:** Required for deployment on Render to bundle Playwright dependencies.

## Local Development (Docker Compose)

The easiest way to run the application locally is via Docker Compose:

1. Clone the repository and copy `.env.example` to `.env`.
2. Fill in the required environment variables in the `.env` file.
3. Build and start the container:

```bash
docker-compose up --build
```

The FastAPI backend and React frontend will be served at `http://localhost:8000`.

## Deployment (Render)

This project is optimized for a single Render Web Service container.

1. Connect your GitHub repository to a new Render Web Service.
2. Choose "Docker" as the runtime environment.
3. Use the included `render.yaml` (Blueprint) or manually add the required environment variables:
   - `GOOGLE_SHEETS_CREDENTIALS_B64`
   - `GOOGLE_SHEET_ID`
   - `OPENROUTER_API_KEY`

Render will build the multi-stage Dockerfile, installing both Node dependencies (for the React build) and Playwright dependencies (for the FastAPI backend), running them seamlessly as one application.

## Configuration

All non-sensitive application configurations (e.g., Schedules, Search Keywords, Enabled Sources, Prompt overrides) are managed directly via the **Settings** page in the UI, which writes to the "Settings" tab in your Google Sheet.
