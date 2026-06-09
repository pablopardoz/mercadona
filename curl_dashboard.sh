#!/usr/bin/env bash
# Nuevo endpoint total: una sola llamada (1 login + 1 dashboard)
# Uso: API_URL=https://mercadona-w0md.onrender.com/api bash curl_dashboard.sh

API_URL="${API_URL:-https://mercadona-w0md.onrender.com/api}"

# 1. Login (obtener token)
echo "=== 1. POST /api/auth/login ==="
TOKEN=$(curl -s "$API_URL/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"pablo","password":"pablo"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Token: ${TOKEN:0:20}..."

# 2. Dashboard (todo en uno)
echo -e "\n=== 2. GET /api/dashboard/ (con time) ==="
time curl -s "$API_URL/dashboard/" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -80
