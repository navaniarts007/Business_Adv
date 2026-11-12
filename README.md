# Vyapar Mitra: AI Business Advisory

Researched, local business advice for **farmers, artisans, shops/vendors, MSMEs, startups and companies**.

- **Google Gemini API** with **Grounding with Google Search** researches live data (mandi prices, schemes, rules, competitors, market size) before it answers, and cites its sources.
- **Google Maps grounding** is used in "Near me" mode to find nearby mandis, suppliers, banks and offices.
- **Local SQLite DB** (`data/advisor.db`) stores business profiles, all Q&A history, a searchable (FTS5) knowledge base of 37 Indian schemes and playbooks, and a research cache so repeat questions cost nothing.
- **Offline mode**: without an API key, answers come from the local knowledge base.
- Answers in 11 Indian languages, with voice input and read-aloud in the browser.

## Run (Windows)

```powershell
cd D:\Business_Adv
.\run.ps1            # first run creates .venv, installs deps and copies .env
```
Open http://localhost:8000

Manual alternative:
```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Enable live Google research

1. Create a free key at https://aistudio.google.com/apikey
2. Put it in `.env`: `GEMINI_API_KEY=your_key`
3. Restart. The header badge changes to **Live research**.

`GEMINI_MODEL` defaults to `gemini-flash-latest`; `.env` currently uses the faster `gemini-flash-lite-latest`. If a model is retired, overloaded or times out (40 s quick / 120 s research), the app moves on to the next model. Short network drops are retried automatically.

**Sarvam AI fallback.** Set `SARVAM_API_KEY` (and optionally `SARVAM_MODEL`, default `sarvam-105b`) in `.env`. If every Gemini model fails (quota, overload, network), or there is no Gemini key, the question goes to Sarvam's OpenAI-compatible `/v2/chat/completions`. Sarvam is strong in Indian languages, but it cannot search the web, so its answers are marked "Answered by Sarvam AI (fallback)". Order: Gemini + Google Search → Gemini without search → Sarvam → offline knowledge base (only when no key is set).

**Google Search grounding needs quota.** On a free-tier key Google may refuse search grounding with `429`. The app then answers without live search, marks the answer "Not live-researched", and stops trying search for 15 minutes. To get live research, enable billing for the key's project in Google AI Studio.

## Answer modes

| Mode | What it does |
|---|---|
| Quick answer | Short answer plus 3-5 action steps, in simple language |
| Deep research report | Several Google searches, then a report: market, costs table, schemes, competition, risks, 30-60-90 day plan |
| Near me | Uses browser location and Google Maps grounding to find nearby markets, suppliers and offices |

## How an answer is built

```
question + profile (segment, business, location, language)
  -> SQLite FTS5 search of the local knowledge base (schemes, finance, compliance, practices)
  -> last 3 Q&As for this profile (so follow-up questions work)
  -> Gemini + google_search tool (or google_maps tool in Near me mode)
  -> answer + Google sources + search queries -> saved to SQLite history and cache
```

## Project layout

```
app/
  main.py      FastAPI routes (/api/ask, /api/profiles, /api/knowledge, /api/history, /api/status)
  advisor.py   Prompting, Gemini call, grounding/citation extraction, offline fallback
  db.py        SQLite schema, FTS5 knowledge search, history, cache
  seed.py      Starter knowledge base: farmer, artisan, retail, MSME, startup, company schemes
  config.py    .env settings
static/        index.html, styles.css, app.js  (no build step)
data/          advisor.db (created on first run)
```

## API

| Method | Path | Body / query |
|---|---|---|
| POST | `/api/ask` | `{question, profile_id?, mode: quick\|research\|nearby, lat?, lng?}` |
| GET/POST | `/api/profiles` | `{name, segment, business, location, state, language, stage, turnover, details}` |
| PUT/DELETE | `/api/profiles/{id}` | |
| GET | `/api/knowledge?q=&segment=` | full-text search |
| POST/DELETE | `/api/knowledge[/{id}]` | add your own local entries (co-ops, buyers, state schemes) |
| GET/DELETE | `/api/history[?profile_id=]` / `/api/history/{id}` | |

Interactive API docs: http://localhost:8000/docs

## Next steps for production

- WhatsApp bot: point the Meta WhatsApp Cloud API webhook to a small route that calls `advisor.ask()`.
- Live mandi prices: pull the Agmarknet dataset from data.gov.in (free API key) into a `prices` table on a schedule.
- Swap SQLite for PostgreSQL when many users write at the same time.
- Add login before exposing it on the internet. Right now anyone who can reach the server can see every profile.

Scheme amounts in `seed.py` were current as of Budget 2025. The AI is told to check them with live search, and every card links to the official portal.
