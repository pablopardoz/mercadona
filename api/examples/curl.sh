# ============================================================
# Ejemplos cURL para probar la API Flask
# ============================================================
# Requisitos:
#   1. La API corriendo → python app.py  (puerto 5000)
#   2. El .env configurado con Supabase
# ============================================================

# ────────────────────────────────────────────
# 1. HEALTH CHECK
# ────────────────────────────────────────────
curl -s http://localhost:5000/api/health | jq .

# ────────────────────────────────────────────
# 2. LOGIN (obtener token JWT)
# ────────────────────────────────────────────
# Usuario por defecto: pablo / pablo
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "pablo", "password": "pablo"}' | jq .

# ────────────────────────────────────────────
# 3. GUARDAR TOKEN EN VARIABLE (bash)
# ────────────────────────────────────────────
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "pablo", "password": "pablo"}' | jq -r '.token')
echo $TOKEN

# ────────────────────────────────────────────
# 4. KPIs
# ────────────────────────────────────────────
curl -s http://localhost:5000/api/kpis/ \
  -H "Authorization: Bearer $TOKEN" | jq .

# ────────────────────────────────────────────
# 5. STATS — Totales
# ────────────────────────────────────────────
curl -s http://localhost:5000/api/stats/totals \
  -H "Authorization: Bearer $TOKEN" | jq .

# ────────────────────────────────────────────
# 6. STATS — Categorías
# ────────────────────────────────────────────
curl -s http://localhost:5000/api/stats/categories \
  -H "Authorization: Bearer $TOKEN" | jq .

# ────────────────────────────────────────────
# 7. LISTAR TICKETS
# ────────────────────────────────────────────
curl -s http://localhost:5000/api/tickets/ \
  -H "Authorization: Bearer $TOKEN" | jq .

# ────────────────────────────────────────────
# 8. DETALLE DE UN TICKET
# ────────────────────────────────────────────
# Reemplaza HASH con un ticket_hash real del paso 7
curl -s http://localhost:5000/api/tickets/HASH \
  -H "Authorization: Bearer $TOKEN" | jq .

# ────────────────────────────────────────────
# 9. CREAR TICKET MANUAL
# ────────────────────────────────────────────
curl -s -X POST http://localhost:5000/api/tickets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "supermercado": "Mercadona",
    "fecha": "2026-06-08",
    "hora": "12:30",
    "total_gasto": 15.50,
    "lineas": [
      {
        "nombre_normalizado": "Leche semidesnatada 1L",
        "cantidad": 2,
        "precio_unitario": 1.05,
        "precio_total": 2.10,
        "categoria": "Lácteos y Huevos",
        "subcategoria": "Leche"
      },
      {
        "nombre_normalizado": "Pan de molde integral",
        "cantidad": 1,
        "precio_unitario": 2.95,
        "precio_total": 2.95,
        "categoria": "Panadería y Pastelería",
        "subcategoria": "Pan"
      }
    ]
  }' | jq .

# ────────────────────────────────────────────
# 10. REGISTRAR NUEVO USUARIO
# ────────────────────────────────────────────
curl -s -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "nuevo_user", "password": "pass123"}' | jq .

# ────────────────────────────────────────────
# 11. SUBIR TICKET PDF (gemini)
# ────────────────────────────────────────────
# Requiere GEMINI_API_KEY configurada en .env
curl -s -X POST http://localhost:5000/api/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/ruta/al/ticket.pdf" | jq .

# ────────────────────────────────────────────
# 12. ERROR — Sin token
# ────────────────────────────────────────────
curl -s http://localhost:5000/api/kpis/ | jq .

# ────────────────────────────────────────────
# 13. ERROR — Token inválido
# ────────────────────────────────────────────
curl -s http://localhost:5000/api/kpis/ \
  -H "Authorization: Bearer token-invalido" | jq .
