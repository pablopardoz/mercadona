#!/usr/bin/env bash
# Llamadas actuales que hace el frontend (7 endpoints)
# Uso: API_URL=https://mercadona-w0md.onrender.com/api bash curls_front.sh

API_URL="${API_URL:-https://mercadona-w0md.onrender.com/api}"

# 1. Login (obtener token)
echo "=== 1. POST /api/auth/login ==="
TOKEN=$(curl -s "$API_URL/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"pablo","password":"pablo"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Token: ${TOKEN:0:20}..."

# 2. KPIs
echo -e "\n=== 2. GET /api/kpis/ ==="
curl -s "$API_URL/kpis/" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

# 3. Stats totals
echo -e "\n=== 3. GET /api/stats/totals ==="
curl -s "$API_URL/stats/totals" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -20

# 4. Stats categories
echo -e "\n=== 4. GET /api/stats/categories ==="
curl -s "$API_URL/stats/categories" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -20

# 5. Tickets list
echo -e "\n=== 5. GET /api/tickets/ ==="
TICKETS_JSON=$(curl -s "$API_URL/tickets/" -H "Authorization: Bearer $TOKEN")
echo "$TICKETS_JSON" | python3 -m json.tool | head -20

# 6. Ticket detail (para cada ticket)
echo -e "\n=== 6. GET /api/tickets/<hash> (primer ticket) ==="
FIRST_HASH=$(echo "$TICKETS_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['tickets'][0]['ticket_hash'])")
curl -s "$API_URL/tickets/$FIRST_HASH" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30
