# API Dashboard Tickets

API Flask con DuckDB para gestionar tickets de compra, estadísticas y KPIs.

## Requisitos

- Python 3.10+
- DuckDB (se instala automáticamente)

## Instalación

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Arranque

```bash
cd api
venv/bin/python app.py
```

El servidor arranca en `http://localhost:5000`.

En el primer arranque, si existe `../public/gastos.duckdb`, importa automáticamente
los tickets y líneas existentes asignándolos al usuario `pablo`.

## Usuario inicial

- **usuario:** `pablo`
- **contraseña:** `pablo`

## Endpoints

Todas las rutas devuelven JSON. Las rutas marcadas con 🔒 requieren
cabecera `Authorization: Bearer <token>`.

### Autenticación

```
POST /api/auth/login    { "username": "...", "password": "..." }  → { token, user }
POST /api/auth/register { "username": "...", "password": "..." }  → 201  🔒
PUT  /api/auth/user     { "username"?: ..., "password"?: ... }    → { user }  🔒
GET  /api/auth/me                                                  → { user }  🔒
POST /api/auth/logout                                              → { message }  🔒
```

### Tickets

```
GET    /api/tickets/?limit=100&offset=0         → { tickets: [...] }  🔒
GET    /api/tickets/<ticket_hash>               → { ticket, lineas }  🔒
POST   /api/tickets/       { supermercado, fecha, hora?, total_gasto?, lineas: [...] }  🔒
DELETE /api/tickets/<ticket_hash>               → { message }  🔒
```

### Estadísticas

```
GET /api/stats/totals       → { resumen, por_mes, por_anio }  🔒
GET /api/stats/categories   → { por_categoria, por_subcategoria }  🔒
```

### KPIs

```
GET /api/kpis/  → { producto_mas_caro, producto_mas_comprado, ... }  🔒
```

### Subida de tickets (PDF con IA)

```
POST /api/upload/  → { message, ticket_hash, ticket }  🔒
```

Sube un PDF de ticket de supermercado. Se procesa con Gemini (`gemini-2.5-flash`)
extrayendo y normalizando productos, categorías y subcategorías. Requiere
`GEMINI_API_KEY` en `.env` (ver `.env.example`).

## Configuración de IA

Copia el `.env` de la raíz del proyecto o créalo:

```bash
GEMINI_API_KEY=tu_clave_de_gemini
```

## Pruebas rápidas con curl

Colección de comandos listos para copiar y pegar contra `localhost:5000`.

### 1. Health check

```bash
curl -s http://localhost:5000/api/health | python3 -m json.tool
```

### 2. Login (obtener token)

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"pablo","password":"pablo"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "TOKEN=$TOKEN"
```

### 3. Ver usuario actual

```bash
curl -s http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 4. Listar tickets

```bash
curl -s "http://localhost:5000/api/tickets/?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 5. Detalle de un ticket

```bash
HASH=$(curl -s "http://localhost:5000/api/tickets/?limit=1" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['tickets'][0]['ticket_hash'])")
curl -s "http://localhost:5000/api/tickets/$HASH" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 6. Crear un ticket

```bash
curl -s -X POST http://localhost:5000/api/tickets/ \
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
  }' | python3 -m json.tool
```

### 7. Eliminar un ticket

```bash
HASH=$(curl -s "http://localhost:5000/api/tickets/?limit=1" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['tickets'][0]['ticket_hash'])")
curl -s -X DELETE "http://localhost:5000/api/tickets/$HASH" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 8. Estadísticas

```bash
curl -s http://localhost:5000/api/stats/totals \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

```bash
curl -s http://localhost:5000/api/stats/categories \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9. KPIs

```bash
curl -s http://localhost:5000/api/kpis/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 10. Registrar nuevo usuario

```bash
curl -s -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}' | python3 -m json.tool
```

### 11. Subir ticket en PDF (procesado con IA)

```bash
curl -s -X POST http://localhost:5000/api/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/ruta/al/ticket.pdf" | python3 -m json.tool
```

### 12. Logout

```bash
curl -s -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Estructura del proyecto

```
api/
├── app.py              # Punto de entrada Flask
├── config.py           # Configuración
├── database.py         # Conexión DuckDB, tablas, consultas
├── decorators.py       # Decorador jwt_required
├── auth.py             # Blueprint de autenticación
├── tickets.py          # Blueprint de tickets
├── stats.py            # Blueprint de estadísticas
├── kpis.py             # Blueprint de KPIs
├── upload.py           # Blueprint de subida de PDF con IA
├── requirements.txt    # Dependencias Python
├── README.md           # Este archivo
└── test.sh             # Script de pruebas con curl
```
