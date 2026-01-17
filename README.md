# Cyprus Transport Hackaton

A digital display system for Cyprus bus stops showing real-time bus arrivals alongside rotating ads, government news, and transport alerts.

![Display Screenshot](display-screenshot.png)

## Features

- **Real-time Bus Arrivals**: Scraped from Motion website with GTFS data enrichment
- **Advertisement Slideshow**: Upload and manage ad images with configurable display duration
- **Government News**: Bilingual slides (Greek on top, English on bottom)
- **Transport Alerts**: Service disruption notices with severity levels
- **50/50 Split Display**: Bus arrivals on left, ads/news on right
- **Progress Bar**: Shows time remaining until next slide

## Tech Stack

- **Backend**: Python 3.13, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js 16.1, React 19, Tailwind CSS, shadcn/ui
- **Infrastructure**: Docker Compose

## Quick Start

### 1. Start with Docker Compose

```bash
docker compose up -d
```

### 2. Sync GTFS Data

```bash
curl -X POST http://localhost:8000/api/gtfs/sync
```

### 3. Access the Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## API Endpoints

### Arrivals
- `GET /api/arrivals/{stop_id}` - Get real-time arrivals for a stop

### Ads
- `GET /api/ads` - List all ads
- `POST /api/ads` - Create ad (multipart form with image)
- `PUT /api/ads/{id}` - Update ad
- `DELETE /api/ads/{id}` - Delete ad

### News (Bilingual)
- `GET /api/news` - List all news
- `POST /api/news` - Create news item (title_el, content_el, title_en, content_en)
- `PUT /api/news/{id}` - Update news
- `DELETE /api/news/{id}` - Delete news

### Alerts
- `GET /api/alerts` - List all alerts
- `GET /api/alerts/stop/{stop_id}` - Get alerts for specific stop
- `POST /api/alerts` - Create alert
- `PUT /api/alerts/{id}` - Update alert
- `DELETE /api/alerts/{id}` - Delete alert

### Content
- `GET /api/content` - Get all active content (ads, news, alerts)

## Display Pages

Access display screens at:
```
http://localhost:3001/display/{stop_id}
```

Example stop IDs (4-digit integers from GTFS):
- `4000` - Pafou - Monovolikos 1
- `6300` - 1 Apriliou - 17th Stop
- `4338` - 1 Apriliou - 5th Kyperounta 1

## Admin Pages

- `/admin/ads` - Manage advertisements
- `/admin/news` - Manage government news
- `/admin/alerts` - Manage transport alerts

## GTFS Data

GTFS data is downloaded directly from `motionbuscard.org.cy/opendata` and imported into the database.
Real-time arrivals are scraped from `motionbuscard.org.cy`.

### GTFS Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/gtfs/cities` | GET | List available cities |
| `/api/gtfs/download` | POST | Download GTFS ZIP files |
| `/api/gtfs/import` | POST | Import GTFS data to database |
| `/api/gtfs/sync` | POST | Download + Import in one step |
| `/api/gtfs/stats` | GET | Get database statistics |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DB_USER | hackaton | PostgreSQL username |
| DB_PASSWORD | hackaton_password | PostgreSQL password |
| DB_DATABASE | bus_hackaton | Database name |
| DB_HOST | postgres | Database host |
| DB_PORT | 5433 | Database port |
| BACKEND_PORT | 8000 | Backend API port |
| FRONTEND_PORT | 3001 | Frontend port |
| NEXT_PUBLIC_API_URL | http://localhost:8000 | API URL for frontend |

## License

MIT
