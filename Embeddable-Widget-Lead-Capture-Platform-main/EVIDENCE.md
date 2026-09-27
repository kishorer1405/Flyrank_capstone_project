# EVIDENCE — FlyRank Capstone

This file is intentionally **not pre-filled with fabricated PASS results**. The official capstone brief requires one real proof per requirement and says claims without evidence score as not done. Run each probe locally and paste the actual output below.

## Environment

- Date tested: `[YYYY-MM-DD]`
- Git commit: `[commit]`
- API base URL: `http://localhost:8000`
- Customer origin: `http://localhost:5500`

## Probe 1 — Valid second-origin submission
**Requirement:** Valid submission is stored and visible through dashboard API.

**Procedure:** Open `http://localhost:5500`, submit the embedded form, then authenticate and call `/api/v1/dashboard/submissions`.

**Expected:** 2xx; stored row; visible in dashboard.

**Actual output:**
```text
[PASTE REAL OUTPUT HERE]
```
**Status:** TODO

## Probe 2 — Malformed and oversized payloads
**Requirement:** Clean 4xx JSON errors, never unexpected 500.

**Procedure:** Send malformed JSON/unknown fields and a body larger than 16 KiB.

**Expected:** 4xx JSON response.

**Actual:**
```text
[PASTE REAL OUTPUT HERE]
```
**Status:** TODO

## Probe 3 — Rate limiting
**Requirement:** Burst returns 429 and service continues serving legitimate traffic.

**Procedure:** Send 6 rapid submissions from one IP/widget with default `5/minute`.

**Expected:** at least one 429; later legitimate request succeeds after the window.

**Actual:**
```text
[PASTE REAL OUTPUT HERE]
```
**Status:** TODO

## Probe 4 — Geo fallback A → B → no geo
**Requirement:** Provider A down uses B; both down still stores submission.

**Procedure:**
1. Set `GEO_PROVIDER_A_MODE=mock_down`, `GEO_PROVIDER_B_MODE=mock_up`, restart API.
2. Submit; inspect dashboard/database and confirm `geo_provider=provider_b`.
3. Set both to `mock_down`, restart API.
4. Submit; confirm row exists with null geo.

**Actual:**
```text
[PASTE REAL OUTPUT HERE]
```
**Status:** TODO

## Probe 5 — Side-effect failure
**Requirement:** Failing notification does not prevent storage/success.

**Procedure:** Set `SIDE_EFFECT_FAIL=true`, restart API/worker, submit valid form.

**Expected:** submission API succeeds and database row remains; worker eventually marks job failed after retries.

**Actual:**
```text
[PASTE REAL OUTPUT HERE]
```
**Status:** TODO

## Probe 6 — Honeypot
**Requirement:** Filled honeypot is rejected or silently dropped.

**Procedure:** POST with a non-empty `honeypot` value.

**Expected:** 400 in this implementation and no submission row created.

**Actual:**
```text
[PASTE REAL OUTPUT HERE]
```
**Status:** TODO

## Widget management
**Test:** register/login + create/list/get/update/delete widget.
**Expected:** 201/200/204 and unauthenticated requests rejected.
**Actual:** `[PASTE REAL OUTPUT]`
**Status:** TODO

## Tenant isolation
**Test:** Tenant B requests Tenant A widget/submissions.
**Expected:** widget returns 404; dashboard contains only B data.
**Actual:** `[PASTE REAL OUTPUT]`
**Status:** TODO

## Delivery caching/versioning
**Test:** GET `/widget.v1.js` and public config.
**Expected:** `Cache-Control` contains max-age; JS response has immutable/version header; config payload is small.
**Actual:** `[PASTE REAL OUTPUT]`
**Status:** TODO

## CORS + OPTIONS
**Test:** OPTIONS `/api/v1/public/submissions` with Origin `http://localhost:5500`.
**Expected:** 204 and `Access-Control-Allow-Origin: http://localhost:5500`.
**Actual:** `[PASTE REAL OUTPUT]`
**Status:** TODO

## Background job + retries
**Test:** inspect worker logs/jobs table after submission and forced failure.
**Expected:** pending → running → completed or retry → failed; submission unaffected.
**Actual:** `[PASTE REAL OUTPUT]`
**Status:** TODO

## Idempotency
**Test:** POST the same widget + `Idempotency-Key` twice.
**Expected:** second response has `duplicate: true` and same submission ID.
**Actual:** `[PASTE REAL OUTPUT]`
**Status:** TODO

## Shared requirements

- Layered architecture: **TODO — explain in review/demo.**
- Boundary validation: **TODO — attach Probe 2 output.**
- ≥1 background job: **TODO — attach worker output.**
- Real persistence/migrations/indexes/tenant isolation: **TODO — attach migration + DB evidence.**
- Idempotency where it matters: **TODO — attach idempotency output.**
- Secrets clean: **TODO — verify `.env` ignored and no secrets committed.**
- AI cost: **Not applicable to runtime — no AI API is used by this application.**
