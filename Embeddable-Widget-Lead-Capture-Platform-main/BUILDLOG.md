# BUILDLOG

## Purpose
This log is intended to stay honest. The capstone brief explicitly says AI-assisted building is encouraged but the intern must record where AI helped, where it was wrong, what was changed, and be able to explain the code.

## 2026-09-13 — Initial complete implementation draft

### What was built
- FastAPI application with JWT authentication and secure password hashing.
- Multi-tenant widget CRUD with service/repository separation.
- Versioned public widget bundle and cached public configuration.
- Second-origin customer demonstration page.
- Public submission API with Pydantic boundary validation, CORS, rate limiting and honeypot protection.
- IP geolocation provider abstraction with A→B fallback and deterministic mock modes.
- PostgreSQL persistence, Alembic migration and indexes.
- PostgreSQL-backed background job worker with retries.
- Non-blocking console notification side effect with deterministic failure switch.
- Idempotency key protection.
- Dashboard submission list and analytics.
- Automated tests for core acceptance behavior.
- README, EVIDENCE, capstone manifest and environment template.

### AI assistance
AI was used to generate and review the initial implementation structure and code. The user must review and test the code locally and should add future entries describing any corrections discovered during their testing. No claim of zero errors is made.

### Important design decisions
1. PostgreSQL is the production/local evaluation database.
2. The worker queue is PostgreSQL-backed to avoid unnecessary Redis/RQ dependency bloat while still meeting the genuine background-job requirement.
3. Rate limiting is in-memory and keyed by client IP + widget; this is appropriate for the single-instance local evaluator but would need a shared store for horizontally scaled production.
4. Geo providers have `real`, `mock_up`, and `mock_down` modes to make fallback tests deterministic.
5. Console notification is used because the official brief explicitly permits a fake/local email side effect.

### Testing status
The codebase includes automated tests, but **no test result is claimed here until the environment where the project is run executes `pytest -q`**. Update this section with actual results.
