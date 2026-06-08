#!/usr/bin/env bash
# Script de pruebas para la API Dashboard Tickets
# Requiere: curl, python3
# Uso: bash test.sh

set -euo pipefail

BASE="${1:-http://localhost:5000}"
TOKEN=""

echo "══════════════════════════════════════════"
echo "  API Dashboard Tickets — Pruebas"
echo "  Base URL: $BASE"
echo "══════════════════════════════════════════"
echo ""

# ── Health ─────────────────────────────────────────────────────
echo "── 1. Health ──────────────────────────────────────────────"
curl -s "$BASE/api/health" | python3 -m json.tool
echo ""

# ── Login ──────────────────────────────────────────────────────
echo "── 2. Login (pablo / pablo) ───────────────────────────────"
RESP=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"pablo","password":"pablo"}')
echo "$RESP" | python3 -m json.tool
TOKEN=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo ""

# ── Me ─────────────────────────────────────────────────────────
echo "── 3. GET /api/auth/me ────────────────────────────────────"
curl -s "$BASE/api/auth/me" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# ── Register (nuevo usuario) ──────────────────────────────────
echo "── 4. POST /api/auth/register (nuevo usuario) ─────────────"
curl -s -X POST "$BASE/api/auth/register" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}' | python3 -m json.tool
echo ""

# ── Listar tickets ─────────────────────────────────────────────
echo "── 5. GET /api/tickets/ ───────────────────────────────────"
curl -s "$BASE/api/tickets/" -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Total tickets: {len(d[\"tickets\"])}')
for t in d['tickets'][:5]:
    print(f'  · {t[\"fecha\"]} | {t[\"supermercado\"]:20s} | {t[\"total_gasto\"]:>8}€')
"
echo ""

# ── Detalle del primer ticket ──────────────────────────────────
echo "── 6. GET /api/tickets/<hash> (primer ticket) ─────────────"
HASH=$(curl -s "$BASE/api/tickets/" -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['tickets'][0]['ticket_hash'])")
curl -s "$BASE/api/tickets/$HASH" -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Supermercado: {d[\"ticket\"][\"supermercado\"]}')
print(f'Fecha: {d[\"ticket\"][\"fecha\"]}')
print(f'Total: {d[\"ticket\"][\"total_gasto\"]}€')
print(f'Productos: {len(d[\"lineas\"])}')
for l in d['lineas'][:5]:
    print(f'  · {l[\"nombre_normalizado\"]:30s} {l[\"cantidad\"]} x {l[\"precio_unitario\"]}€ = {l[\"precio_total\"]}€')
if len(d['lineas']) > 5:
    print(f'  ... y {len(d[\"lineas\"])-5} más')
"
echo ""

# ── Crear ticket ──────────────────────────────────────────────
echo "── 7. POST /api/tickets/ (crear ticket) ───────────────────"
CREATED_RESP=$(curl -s -X POST "$BASE/api/tickets/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "supermercado": "Mercadona",
    "fecha": "2026-06-05",
    "hora": "10:30",
    "total_gasto": 12.50,
    "lineas": [
      {"nombre_normalizado": "Leche semidesnatada", "cantidad": 2, "precio_unitario": 1.05, "categoria": "Lácteos y Huevos", "subcategoria": "Leche"},
      {"nombre_normalizado": "Pan de molde", "cantidad": 1, "precio_unitario": 2.20, "categoria": "Panadería", "subcategoria": "Pan"},
      {"nombre_normalizado": "Manzanas Golden", "cantidad": 1.5, "precio_unitario": 2.50, "categoria": "Frutas y Verduras", "subcategoria": "Frutas"}
    ]
  }')
echo "$CREATED_RESP" | python3 -m json.tool
CREATED_HASH=$(echo "$CREATED_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_hash',''))" 2>/dev/null || echo "")
echo ""

# ── Stats totals ──────────────────────────────────────────────
echo "── 8. GET /api/stats/totals ───────────────────────────────"
curl -s "$BASE/api/stats/totals" -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
r=d['resumen']
total = float(r['total_global'])
print(f'Total global: {total}€')
print(f'Número tickets: {r[\"num_tickets\"]}')
print(f'Media por ticket: {total/r[\"num_tickets\"]:.2f}€')
print(f'Meses con gasto: {len(d[\"por_mes\"])}')
for m in d['por_mes']:
    print(f'  · {m[\"mes\"]}: {m[\"total\"]}€ ({m[\"num_tickets\"]} tickets)')
"
echo ""

# ── Stats categories ──────────────────────────────────────────
echo "── 9. GET /api/stats/categories ───────────────────────────"
curl -s "$BASE/api/stats/categories" -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
print('Categorías:')
for c in d['por_categoria']:
    print(f'  · {c[\"categoria\"]:30s} {c[\"total\"]:>8}€  ({c[\"num_productos\"]} prod.)')
"
echo ""

# ── KPIs ──────────────────────────────────────────────────────
echo "── 10. GET /api/kpis/ ─────────────────────────────────────"
curl -s "$BASE/api/kpis/" -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
pc = d['producto_mas_caro']
print(f'Producto más caro: {pc[\"nombre_normalizado\"]} — {pc[\"precio_unitario\"]}€ ({pc[\"supermercado\"]})')
pm = d['producto_mas_comprado']
print(f'Producto más comprado: {pm[\"nombre_normalizado\"]} — {pm[\"total_cantidad\"]} uds. en {pm[\"veces\"]} tickets')
pf = d['producto_mas_frecuente']
print(f'Producto más frecuente: {pf[\"nombre_normalizado\"]} — {pf[\"veces\"]} tickets')
pv = d['producto_mas_variable']
if pv:
    print(f'Mayor variación precio: {pv[\"nombre_normalizado\"]} — de {pv[\"precio_min\"]}€ a {pv[\"precio_max\"]}€ (diff {pv[\"diff\"]}€)')
sv = d['super_mas_visitado']
print(f'Supermercado más visitado: {sv[\"supermercado\"]} — {sv[\"veces\"]} visitas ({sv[\"total\"]}€)')
print('Top 5 productos por gasto:')
for p in d['top_productos']:
    print(f'  · {p[\"nombre_normalizado\"]:30s} {p[\"total_gasto\"]:>8}€  ({p[\"veces\"]} tickets)')
"
echo ""

# ── Eliminar el ticket creado ─────────────────────────────────
echo "── 11. DELETE /api/tickets/<hash> (limpieza) ──────────────"
if [ -n "$CREATED_HASH" ]; then
  curl -s -X DELETE "$BASE/api/tickets/$CREATED_HASH" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
else
  echo "  (no se pudo obtener el hash para limpiar)"
fi
echo ""

echo "══════════════════════════════════════════"
echo "  ✅ Pruebas completadas"
echo "══════════════════════════════════════════"
