# Bus Signage - Cyprus Digital Displays

A SaaS platform for bus stop digital signage displays showing real-time bus arrivals alongside rotating ads, government news, and transport alerts.

## Features

- **Real-time Bus Arrivals**: Scraped from Motion website with GTFS data enrichment
- **Advertisement Slideshow**: Upload and manage ad images with configurable display duration
- **Government News**: Ticker display for government announcements
- **Transport Alerts**: Service disruption notices with severity levels
- **50/50 Split Display**: Bus arrivals on left, ads/news on right

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Display Screen                            │
├─────────────────────────────┬───────────────────────────────┤
│                             │                               │
│     BUS ARRIVALS            │     ADS / NEWS                │
│                             │                               │
│  [Alert Banner if any]      │   ┌───────────────────────┐   │
│                             │   │                       │   │
│  Route 30  →  5 min         │   │   Ad Image            │   │
│  Route 15  →  12 min        │   │   (slideshow)         │   │
│  Route 7   →  18 min        │   │                       │   │
│                             │   └───────────────────────┘   │
│                             │                               │
│  Stop: Makariou Avenue      │   Government News Ticker      │
│                             │                               │
└─────────────────────────────┴───────────────────────────────┘
```

## Tech Stack

- **Backend**: Python 3.13, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js 14, React, Tailwind CSS, shadcn/ui
- **Infrastructure**: Docker Compose

## Quick Start

### 1. Clone and Setup

```bash
cd bus-signage
cp env.example .env
```

### 2. Start with Docker Compose

```bash
docker compose up -d
```

### 3. Access the Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Development

### Backend Only

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Only

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Arrivals
- `GET /api/arrivals/{stop_id}` - Get real-time arrivals for a stop

### Ads
- `GET /api/ads` - List all ads
- `POST /api/ads` - Create ad (multipart form with image)
- `PUT /api/ads/{id}` - Update ad
- `DELETE /api/ads/{id}` - Delete ad

### News
- `GET /api/news` - List all news
- `POST /api/news` - Create news item
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

Example stop IDs:
- `LIM-001` - Limassol
- `NIC-001` - Nicosia
- `LAR-001` - Larnaca

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
| DB_USER | signage | PostgreSQL username |
| DB_PASSWORD | signage_password | PostgreSQL password |
| DB_DATABASE | bus_signage | Database name |
| DB_HOST | postgres | Database host |
| DB_PORT | 5433 | Database port |
| BACKEND_PORT | 8000 | Backend API port |
| FRONTEND_PORT | 3001 | Frontend port |
| NEXT_PUBLIC_API_URL | http://localhost:8000 | API URL for frontend |

## License

MIT
