#!/usr/bin/env bash
set -euo pipefail
curl -fsS http://localhost:8000/health
printf "\nWidget bundle headers:\n"
curl -sSI "http://localhost:8000/widget.v1.js"
printf "\nCORS preflight:\n"
curl -sSI -X OPTIONS "http://localhost:8000/api/v1/public/submissions" -H "Origin: http://localhost:5500" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type,idempotency-key"
