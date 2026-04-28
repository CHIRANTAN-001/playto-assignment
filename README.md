# Playto Pay — Payout Engine

A minimal payout engine for Indian agencies and freelancers to collect international payments. Merchants accumulate balance from customer payments (credits) and withdraw to their Indian bank accounts (debits/payouts).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0, Django REST Framework |
| Frontend | React 19, TypeScript, Tailwind CSS, Vite |
| Database | PostgreSQL 18 |
| Background Jobs | Celery + Redis |
| Scheduler | Celery Beat (django-celery-beat) |
| Containerization | Docker, Docker Compose |

## Quick Start (Docker)

The fastest way to run everything:

```bash
git clone <repo-url> && cd playto-assignment

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services (Postgres, Redis, Backend, Celery Worker, Celery Beat, Frontend)
docker compose up --build
```

The entrypoint automatically runs migrations and seeds test data.

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/v1
- **Health check:** http://localhost:8000/health/

### Seeded Test Merchants

| Name | Email | Balance |
|------|-------|---------|
| John Doe | john.doe@example.com | ₹3,50,000 |
| Jane Doe | jane.doe@example.com | ₹6,50,000 |

Login on the dashboard using any of these emails.

## Manual Setup (without Docker)

### Prerequisites

- Python 3.13+
- Node.js 22+
- PostgreSQL 18+
- Redis 7+

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Postgres and Redis credentials

# Run migrations
python manage.py migrate

# Seed test data
python manage.py seed

# Start the server
python manage.py runserver
```

### Celery Worker & Beat

In separate terminals (with the venv activated):

```bash
# Worker — processes payout tasks
celery -A config worker --loglevel=info --pool=solo

# Beat — schedules retry checks every 10s
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start dev server
npm run dev
```

Frontend runs at http://localhost:5173.

## Running Tests

```bash
cd backend

# Run all tests
python manage.py test tests

# Run specific tests
python manage.py test tests.test_concurrency
python manage.py test tests.test_idempotency
```

### Test Coverage

| Test | What it verifies |
|------|-----------------|
| `test_concurrency` | Two simultaneous ₹60 payouts on ₹100 balance — exactly one succeeds, one is rejected |
| `test_idempotency` | Same idempotency key sent twice — only one payout created, same response returned |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payouts/` | Create a payout (requires `Idempotency-Key` header) |
| GET | `/api/v1/payouts/<id>/` | Get payout by ID |
| GET | `/api/v1/merchants/<id>/balance/` | Get merchant balance (available + held) |
| GET | `/api/v1/merchants/<id>/payouts/` | List merchant payouts (cursor-paginated) |
| GET | `/api/v1/merchants/<id>/ledger/` | List ledger entries (cursor-paginated) |
| GET | `/api/v1/merchants/<id>/bank-accounts/` | List merchant bank accounts |
| POST | `/api/v1/merchants/login/` | Merchant lookup by email |

### Example: Create a Payout

```bash
curl -X POST http://localhost:8000/api/v1/payouts/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{"amount_paise": 100000, "bank_account_id": "<uuid>"}'
```

## Project Structure

```
playto-assignment/
├── backend/
│   ├── config/          # Django settings, URLs, Celery config
│   ├── merchants/       # Merchant & BankAccount models, views, seed command
│   ├── ledger/          # Ledger model, balance calculation (DB-level)
│   ├── payouts/         # Payout model, state machine, services, Celery tasks
│   ├── idempotencykey/  # Idempotency key model & services
│   ├── common/          # UUIDv7, health checks, startup hooks
│   ├── tests/           # Concurrency & idempotency tests
│   └── api/v1/          # URL routing
├── frontend/
│   ├── src/
│   │   ├── components/  # BalanceCards, PayoutForm, PayoutTable, LedgerTable
│   │   ├── hooks/       # React Query hooks with polling
│   │   ├── pages/       # LoginPage, DashboardPage
│   │   └── api/         # Axios client
│   └── ...
├── docker-compose.yml   # 6-service orchestration
├── EXPLAINER.md         # Technical deep-dive
└── README.md
```

## Architecture Decisions

- **Paise as BigIntegerField** — no floats, no decimals. All money is stored as integers in paise.
- **Balance derived from ledger** — no cached balance column. `SUM(credits) - SUM(debits)` is the source of truth, computed at the database level.
- **Merchant row lock for concurrency** — `SELECT FOR UPDATE` on the Merchant row serializes all payout requests per merchant.
- **State machine on the model** — `VALID_TRANSITIONS` dict + `transition_to()` method. Terminal states (`completed`, `failed`) block all outgoing transitions.
- **Celery for async processing** — payouts are dispatched via `transaction.on_commit()` to avoid processing before the DB commit.
- **Cursor-based pagination** — UUIDv7 IDs are time-ordered, so `id < cursor` gives stable pagination without offset drift.

## Live Deployment

| Service | URL |
|---------|-----|
| **Frontend** | https://playto-assignment-psi.vercel.app/ |
| **Backend API** | https://api.playto.zebnox.in/ |

### How to Use

Login with one of the seeded merchant emails:
- `john.doe@example.com`
- `jane.doe@example.com`

This applies to both the live deployment and local setup.

### Deployment Note

The backend was initially deployed on Railway, which placed the server in an EU region while the PostgreSQL and Redis were also hosted in India (Bangalore). The cross-continent network round-trip added 2-4 seconds of latency per DB query, making the app unusable. To fix this, I hosted the backend server on AWS (India region) with an SSL certificate. PostgreSQL and Redis are also hosted on DigitalOcean (India region), so all three services are co-located in the same region. This brought the round-trip latency down from seconds to milliseconds(200 - 500ms).
