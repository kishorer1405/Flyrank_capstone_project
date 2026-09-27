# FlyRank Embeddable Widget & Lead-Capture Platform

> **Backend Engineering Capstone — Production-style multi-tenant lead capture platform**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Persistence-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-7%20passed-success)](#testing)
[![License](https://img.shields.io/badge/license-MIT-black)](LICENSE)

A professional, backend-focused implementation of the **FlyRank Embeddable Widget & Lead-Capture Platform** capstone. The system allows authenticated tenant owners to create widgets, embed them on a separate customer website, capture leads securely across origins, enrich submissions with IP geolocation, protect the public endpoint from abuse, and inspect tenant-scoped analytics through a lightweight dashboard.

The project is intentionally designed around **clean separation of concerns, real persistence, secure tenant isolation, reliable background processing, deterministic evaluator probes, and straightforward local deployment**.

---

## 📌 Project at a Glance

| Area | Implementation |
|---|---|
| **API framework** | Python + FastAPI |
| **Database** | PostgreSQL + SQLAlchemy |
| **Migrations** | Alembic |
| **Authentication** | JWT bearer authentication |
| **Validation** | Pydantic boundary validation |
| **Widget delivery** | Versioned JavaScript bundle |
| **Cross-origin capture** | Configured CORS + public submission endpoint |
| **Abuse protection** | IP/widget rate limiting + honeypot |
| **Geo enrichment** | Provider A → Provider B → graceful no-geo fallback |
| **Background processing** | PostgreSQL-backed durable job queue + worker |
| **Reliability** | Retry with exponential backoff + failed-job state |
| **Idempotency** | `Idempotency-Key` + database uniqueness constraint |
| **Dashboard** | Lightweight HTML/CSS/JavaScript |
| **Deployment** | Docker Compose |
| **Testing** | Pytest |
| **License** | MIT |

---

## 🎯 Capstone Objectives

The implementation addresses the major requirements from the FlyRank Backend Track Capstone Brief:

- Multi-tenant authenticated widget CRUD
- Tenant-isolated data access
- One-line widget embed snippet
- Public, versioned widget delivery
- Cached public widget configuration
- Customer website hosted on a second origin
- CORS-safe public lead submission
- Boundary validation and malformed/oversized request rejection
- Per-IP/per-widget rate limiting
- Honeypot spam protection
- Deterministic IP geolocation fallback
- Graceful operation when all geo providers fail
- Non-blocking notification side effects
- Durable background jobs with retries
- Idempotent lead submission
- Tenant-scoped dashboard analytics
- PostgreSQL persistence with migrations and indexes
- Dockerized local development
- Evidence and build documentation for evaluator review

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │     Owner Browser    │
                         │  JWT Authenticated   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │ Auth / Widgets       │
                         │ Public / Dashboard   │
                         └───────┬───────┬──────┘
                                 │       │
                       tenant-scoped     │ public
                          persistence     │ traffic
                                 │       │
                                 ▼       ▼
                         ┌──────────────────────┐
                         │     PostgreSQL       │
                         │                      │
                         │ Users                │
                         │ Widgets              │
                         │ Submissions          │
                         │ Background Jobs      │
                         └──────────┬───────────┘
                                    │
                              queued jobs
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Background Worker  │
                         │                      │
                         │ Claim → Process      │
                         │ Retry → Backoff      │
                         │ Fail after attempts  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                              Notification
                              side effect

┌──────────────────────┐
│ Customer Website     │
│ http://localhost:5500│
└──────────┬───────────┘
           │
           │ <script src=".../widget.v1.js?id=...">
           ▼
┌──────────────────────┐
│ Public Widget Bundle │
└──────────┬───────────┘
           │
           ├── GET public config
           │
           └── POST lead submission
                 │
                 ├── Validation
                 ├── Rate limit
                 ├── Honeypot
                 ├── Geo A → Geo B → no geo
                 ├── Persist submission
                 └── Queue notification job
```

### Layer responsibilities

| Layer | Responsibility |
|---|---|
| **API** | HTTP routing, authentication dependencies, status codes, CORS and request boundaries |
| **Schemas** | Typed request/response contracts and input validation |
| **Services** | Business rules, tenant ownership, submission workflow, geo fallback and side effects |
| **Repositories** | Database access and tenant-scoped queries |
| **Models** | PostgreSQL domain model |
| **Migrations** | Versioned database schema changes |
| **Worker** | Durable background job processing and retries |
| **Widget** | Embeddable customer-facing lead form |
| **Dashboard** | Lightweight owner-facing analytics interface |

---

## 🔐 Security & Reliability

### Authentication & tenant isolation

- Owner endpoints require JWT bearer authentication.
- Passwords are hashed and plaintext credentials are never logged.
- Widget and submission queries are scoped to the authenticated tenant.
- Tenant IDs are persisted and used in database/dashboard queries rather than relying on frontend filtering.
- Invalid or expired JWTs are rejected with `401 Unauthorized`.

### Request protection

- Pydantic validates requests at the API boundary.
- Required fields and field lengths are enforced.
- Unknown submission fields are rejected.
- Public request bodies are limited to **16 KiB** by configuration.
- Rate limiting is applied using the requesting IP and widget identifier.
- Honeypot submissions are rejected before geo enrichment.
- CORS allows only configured customer origins.

### Reliable side effects

Lead persistence does **not** depend on successful notification delivery.

```text
HTTP request
     │
     ▼
Validate → Protect → Enrich → Store lead
                              │
                              └── Queue notification job
                                         │
                                         ▼
                                    Worker process
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                           Success              Failure
                                                    │
                                             Retry + backoff
                                                    │
                                             Max attempts
                                                    │
                                                    ▼
                                                 Failed
```

If the notification side effect fails, the lead remains persisted and the original submission can still succeed.

---

## 🌍 Geo-Enrichment Fallback

The submission workflow supports a deterministic fallback chain:

```text
Provider A
   │
   ├── success ───────────────► store geo data
   │
   └── failure
          │
          ▼
      Provider B
          │
          ├── success ────────► store geo data
          │
          └── failure
                 │
                 ▼
             store lead
             without geo
```

The environment supports deterministic development/evaluation modes:

- `mock_up` — provider responds successfully
- `mock_down` — provider intentionally fails
- `real` — use the configured external provider

This allows evaluator probes to verify **A → B fallback** and **all-providers-down graceful degradation** without depending on external network availability.

---

## ⚡ Widget Delivery & Caching

The embeddable widget is delivered through a versioned asset:

```html
<script src="http://localhost:8000/widget.v1.js?id=YOUR_WIDGET_ID"></script>
```

The delivery strategy uses:

- Versioned JavaScript (`widget.v1.js`)
- Long-lived cache headers
- `immutable` asset caching
- Short-lived cached public widget configuration
- Widget version incrementing on updates

A future incompatible widget implementation can be introduced as `widget.v2.js` without invalidating the existing v1 bundle.

---

## 🧱 Data Model

```text
users
  │
  │ 1:N
  ▼
widgets
  │
  │ 1:N
  ▼
submissions
  │
  │ 1:1 / 1:N job lifecycle
  ▼
background_jobs
```

### Important persistence rules

- `users` represents tenant/customer owners.
- `widgets` belong to one tenant.
- `submissions` belong to both a widget and its tenant.
- `(widget_id, idempotency_key)` is protected by a database uniqueness constraint.
- `background_jobs` tracks asynchronous notification processing and retry state.
- PostgreSQL indexes support common lookup paths.

---

## 🔁 Idempotency

Clients may send an `Idempotency-Key` header:

```http
Idempotency-Key: demo-lead-001
```

For the same widget and key, a retry returns the existing submission instead of creating another lead.

The application also uses a PostgreSQL uniqueness constraint as a second line of defense against concurrent duplicate submissions.

---

## 📂 Project Structure

```text
flyrank-capstone-widget-platform/
│
├── app/
│   ├── api/                 # FastAPI route modules
│   ├── core/                # Configuration, security, logging
│   ├── db/                  # Database session/base configuration
│   ├── models/              # SQLAlchemy models
│   ├── repositories/        # Tenant-scoped persistence operations
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic
│   ├── utils/               # Shared utilities
│   └── workers/             # Background worker process
│
├── alembic/
│   └── versions/            # Database migrations
│
├── customer-site/           # Second-origin demo customer page
├── dashboard/               # Lightweight owner dashboard
├── widget/                  # Public embeddable widget bundle
├── scripts/                 # Seed and verification scripts
├── tests/                   # Automated capstone tests
│
├── README.md                # Project documentation
├── EVIDENCE.md              # Acceptance-probe evidence
├── BUILDLOG.md              # Build and AI-assistance log
├── capstone.yaml            # Capstone metadata/configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # API container
├── docker-compose.yml       # Local API + PostgreSQL stack
├── alembic.ini              # Alembic configuration
├── .env.example             # Safe environment template
├── .gitignore               # Repository exclusions
└── LICENSE                  # MIT license
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker Desktop
- Git

### Option A — Docker Compose

1. Clone the repository.

2. Create the environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

3. Start the stack:

```bash
docker compose up --build
```

4. In another terminal, seed demo data:

```bash
docker compose exec api python scripts/seed.py
```

5. Open the API documentation:

```text
http://localhost:8000/docs
```

6. Serve the customer site from a **second origin**:

```bash
cd customer-site
python -m http.server 5500
```

7. Put the Widget ID printed by the seed script into `customer-site/index.html` in place of `REPLACE_WITH_WIDGET_ID`.

8. Open:

```text
http://localhost:5500
```

### Option B — Local Python development

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start PostgreSQL with Docker:

```powershell
docker compose up -d db
```

Apply migrations:

```powershell
alembic upgrade head
```

Seed demo data:

```powershell
python scripts/seed.py
```

Start the API:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the background worker in a separate terminal:

```powershell
python -m app.workers
```

Serve the customer site:

```powershell
cd customer-site
python -m http.server 5500
```

Serve the dashboard, if required:

```powershell
cd dashboard
python -m http.server 5501
```

---

## 👤 Demo Credentials

The seed script creates a local evaluation account:

```text
Email:    demo@flyrank.local
Password: Demo@12345
```

> **Security note:** These credentials are intended only for local evaluation. Do not reuse them in a real deployment.

---

## 📡 API Surface

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a tenant owner |
| `POST` | `/api/v1/auth/login` | Authenticate and receive JWT |
| `GET` | `/api/v1/auth/me` | Return current authenticated owner |
| `GET` | `/api/v1/widgets` | List tenant widgets |
| `POST` | `/api/v1/widgets` | Create a widget |
| `GET` | `/api/v1/widgets/{widget_id}` | Retrieve a tenant widget |
| `PATCH` | `/api/v1/widgets/{widget_id}` | Update a tenant widget |
| `DELETE` | `/api/v1/widgets/{widget_id}` | Delete a tenant widget |
| `GET` | `/widget.v1.js?id={widget_id}` | Serve versioned widget bundle |
| `GET` | `/api/v1/public/widgets/{widget_id}/config` | Retrieve cached public config |
| `POST` | `/api/v1/public/submissions` | Capture a public lead |
| `OPTIONS` | `/api/v1/public/submissions` | CORS preflight |
| `GET` | `/api/v1/dashboard/submissions` | Tenant-scoped submissions |
| `GET` | `/api/v1/dashboard/stats` | Dashboard analytics |
| `GET` | `/health` | Service health check |

Interactive API documentation is available through FastAPI Swagger UI at:

```text
http://localhost:8000/docs
```

---

## 🧪 Testing

Run the complete automated test suite with:

```bash
pytest -q
```

Current local result:

```text
7 passed, 7 warnings
```

The tests cover the core capstone workflow, including:

- Authentication
- Widget CRUD
- Tenant isolation
- Public submission validation
- Idempotency
- Honeypot protection
- Rate limiting
- CORS preflight
- Dashboard tenant scoping

The automated suite uses an isolated SQLite test database. Local evaluation/deployment uses PostgreSQL through Docker.

> The deprecation warnings reported by the current dependency versions do not cause test failures.

---

## 🔎 Evaluator Acceptance Probes

The implementation is designed for the evaluator's expected probes:

| Probe | Expected behavior |
|---|---|
| Valid second-origin submission | `201 Created` and lead persisted |
| Malformed submission | `4xx` validation response |
| Oversized payload | `413 Content Too Large` |
| Rate limit exceeded | `429 Too Many Requests` |
| Honeypot/spam | `400 Bad Request` |
| Geo provider A fails | Fall back to provider B |
| Geo providers A+B fail | Lead still stored without geo |
| Side effect fails | Lead remains stored; worker retries independently |
| Idempotent retry | Existing submission returned; no duplicate lead |
| Cross-tenant access | Unauthorized/not-found behavior |
| CORS preflight | Successful `204 No Content` preflight |

Detailed evaluator evidence and reproducible commands are documented in [`EVIDENCE.md`](EVIDENCE.md).

---

## 🧾 Evidence & Build Documentation

### `EVIDENCE.md`

Maps the official acceptance probes to reproducible local commands and expected behavior. Actual evaluator evidence should contain the real command output rather than unsupported claims.

### `BUILDLOG.md`

Documents implementation decisions, development milestones and AI-assisted work honestly, in line with the capstone requirement for transparent AI usage.

### `capstone.yaml`

Contains project/capstone metadata and configuration used by the submission.

---

## ⚙️ Environment Configuration

Configuration is loaded from environment variables. See [`.env.example`](.env.example).

Important settings include:

```text
BASE_URL
DATABASE_URL
JWT_SECRET_KEY
CORS_ALLOWED_ORIGINS
RATE_LIMIT
MAX_PAYLOAD_BYTES
CONFIG_CACHE_SECONDS
WIDGET_CACHE_SECONDS
GEO_PROVIDER_A_URL
GEO_PROVIDER_B_URL
GEO_PROVIDER_A_MODE
GEO_PROVIDER_B_MODE
SIDE_EFFECT_MODE
SIDE_EFFECT_FAIL
JOB_POLL_SECONDS
MAX_JOB_ATTEMPTS
```

### Secret management

- `.env` is git-ignored.
- `.env.example` contains safe configuration placeholders.
- Credentials, JWT secrets and provider secrets should never be committed.

---

## 🧩 Design Decisions & Trade-offs

### 1. In-memory rate limiter

A lightweight in-memory limiter is used because the capstone evaluator runs locally. It is intentionally simple and is **not a distributed limiter for multiple API replicas**.

### 2. PostgreSQL-backed background queue

The worker queue is implemented with PostgreSQL instead of Redis/RQ. This keeps the stack compact while still providing:

- Durable queued jobs
- Separate worker process
- Row-lock based claiming
- Retry tracking
- Exponential backoff
- Failed-job state

### 3. Console notification side effect

The notification sink is intentionally a console/log implementation. The capstone permits a fake/logged side effect, so an external mail service is not required for evaluation.

### 4. Lightweight customer site

The customer page is plain HTML/JavaScript and intentionally runs on a second origin. This keeps the focus on backend integration and cross-origin behavior.

### 5. Lightweight dashboard

The dashboard is intentionally minimal because the capstone evaluates backend engineering rather than frontend design.

---

## 🛠️ Troubleshooting

### Port 8000 is already in use

Stop the process using the port or change the published port and update `BASE_URL` accordingly.

### Widget is unavailable on the customer page

Check:

1. API is running on port `8000`.
2. Customer site is running on port `5500`.
3. The Widget ID is correct.
4. `customer-site/index.html` contains the correct widget ID.

### CORS error

Make sure the exact customer origin is present in `CORS_ALLOWED_ORIGINS`, including scheme, host and port.

### Geo data is missing

Check the provider modes in `.env`. For deterministic evaluation, use `mock_up` and `mock_down` rather than relying on external internet access.

### Background jobs are not completing

Confirm the worker is running:

```powershell
python -m app.workers
```

With Docker:

```bash
docker compose logs worker
```

---

## 📋 Repository Submission Checklist

Before submission, verify:

- [x] Public GitHub repository
- [x] Application source code committed
- [x] Automated tests passing
- [x] PostgreSQL migration included
- [x] Docker configuration included
- [x] Customer second-origin site included
- [x] Dashboard included
- [x] Versioned widget included
- [x] `README.md` included
- [x] `EVIDENCE.md` included
- [x] `BUILDLOG.md` included
- [x] `capstone.yaml` included
- [x] `.env.example` included
- [x] `.env` excluded from Git
- [x] MIT license included

### Submission repository

**FlyRank Embeddable Widget & Lead-Capture Platform**

`https://github.com/kishorer1405/Flyrank_capstone_project`

---

## 📄 License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 🙌 Acknowledgement

Built as a FlyRank Backend Engineering Track capstone project, with AI assistance used as a development aid and documented in [`BUILDLOG.md`](BUILDLOG.md).

## AUTHOR

**KISHORE R**