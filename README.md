# AI-Powered Job Scraping Dashboard

A lightweight, modular, production-ready Job Scraping Dashboard designed to run on **Vercel** serverless architecture. This application automates job searching from multiple sources, filters jobs using an AI model via OpenRouter, and stores accepted jobs and browser sessions securely in Supabase.

## Features

- **Automated Web Scraping:** Uses Playwright to mimic X-Ray searches across job boards (LinkedIn, Greenhouse, Lever, Ashby, etc.).
- **Authenticated Sessions (V2):** Pluggable Connection Manager allows logging into platforms (like LinkedIn) directly from the dashboard. The browser session is encrypted and persisted seamlessly in Supabase, bypassing Vercel's ephemeral filesystem limitations.
- **AI Filtering:** Swappable AI provider (default OpenRouter) evaluates job descriptions based on a customizable prompt and issues Keep/Reject decisions.
- **Supabase Database:** Uses Supabase (PostgreSQL) as the persistence layer.
- **Deduplication:** Normalizes data and prevents duplicates by Job URL and Company+Title signatures.
- **Dashboard UI:** React (Vite) + Tailwind CSS + shadcn/ui dashboard to review statistics, jobs, system health, and configure the application.

## Prerequisites

1. **Supabase Project:** A Supabase project URL and service key for database storage.
2. **OpenRouter API Key:** Used to run the `gpt-oss-20b:free` model for filtering jobs.
3. **Session Encryption Key:** A secure random string to encrypt browser cookies and local storage before saving to the database.

## Deployment (Vercel)

This project is optimized for deployment on Vercel.

1. Connect your GitHub repository to Vercel.
2. The `vercel.json` file will automatically configure:
   - Python Serverless Functions (`api/index.py`).
   - Vite React Frontend build routing.
   - Vercel Cron Jobs (to trigger scraping daily).
3. Set the following Environment Variables in Vercel:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENROUTER_API_KEY`
   - `SESSION_ENCRYPTION_KEY`

**Important Playwright Note for Vercel:** Playwright chromium binaries are large and often exceed Vercel's 250MB serverless deployment limit. To ensure reliable authenticated scraping on Vercel, it is highly recommended to configure Playwright to connect to a cloud browser provider (like Browserless.io) via WebSocket in `linkedin.py` rather than launching local Chromium binaries within the serverless function.

## Configuration

All non-sensitive application configurations (e.g., Schedules, Search Keywords, Enabled Sources, Prompt overrides) are managed directly via the **Settings** page in the UI.
