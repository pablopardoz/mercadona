-- ============================================================
-- DDL — Esquema para tickets de supermercado (Supabase/PostgreSQL)
-- ============================================================
-- Uso: pegar en el SQL Editor de Supabase o ejecutar con psql

-- -----------------------------------------------------------
-- 1. TABLA: usuarios
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id            SERIAL PRIMARY KEY,
  username      VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -----------------------------------------------------------
-- 2. TABLA: supermercados
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS supermarkets (
  id          BIGINT  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre      TEXT    NOT NULL,
  direccion   TEXT,
  coordenadas TEXT
);

-- -----------------------------------------------------------
-- 3. TABLA: tickets
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets (
  id              BIGINT  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticket_hash     TEXT    NOT NULL UNIQUE,
  supermercado    TEXT    NOT NULL,
  fecha           DATE    NOT NULL,
  hora            TEXT,
  total_gasto     NUMERIC(10,2) NOT NULL DEFAULT 0,
  user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  supermarket_id  INTEGER REFERENCES supermarkets(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tickets_fecha          ON tickets (fecha DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_user_id        ON tickets (user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_supermercado   ON tickets (supermercado);
CREATE INDEX IF NOT EXISTS idx_tickets_supermarket_id ON tickets (supermarket_id);

-- -----------------------------------------------------------
-- 4. TABLA: lineas_ticket
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS lineas_ticket (
  id                  BIGINT  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticket_hash         TEXT    NOT NULL REFERENCES tickets(ticket_hash) ON DELETE CASCADE,
  nombre_original     TEXT,
  nombre_normalizado  TEXT    NOT NULL,
  cantidad            NUMERIC(10,3) NOT NULL DEFAULT 1,
  precio_unitario     NUMERIC(10,2) NOT NULL DEFAULT 0,
  precio_total        NUMERIC(10,2) NOT NULL DEFAULT 0,
  categoria           TEXT,
  subcategoria        TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lineas_ticket_hash     ON lineas_ticket (ticket_hash);
CREATE INDEX IF NOT EXISTS idx_lineas_categoria       ON lineas_ticket (categoria);
CREATE INDEX IF NOT EXISTS idx_lineas_subcategoria    ON lineas_ticket (subcategoria);
CREATE INDEX IF NOT EXISTS idx_lineas_normalizado     ON lineas_ticket (nombre_normalizado);

-- -----------------------------------------------------------
-- 5. VISTA: resumen_mensual
-- -----------------------------------------------------------
CREATE OR REPLACE VIEW resumen_mensual AS
SELECT
  t.user_id,
  TO_CHAR(t.fecha, 'YYYY-MM')        AS mes,
  COUNT(*)                            AS num_tickets,
  ROUND(SUM(t.total_gasto)::numeric, 2) AS total_gasto
FROM tickets t
GROUP BY t.user_id, mes
ORDER BY t.user_id, mes;

-- -----------------------------------------------------------
-- 6. VISTA: resumen_categorias
-- -----------------------------------------------------------
CREATE OR REPLACE VIEW resumen_categorias AS
SELECT
  t.user_id,
  l.categoria,
  ROUND(SUM(l.precio_total)::numeric, 2) AS total_gasto,
  COUNT(*)                                AS num_productos,
  ROUND(
    100.0 * SUM(l.precio_total) / NULLIF(SUM(SUM(l.precio_total)) OVER (PARTITION BY t.user_id), 0),
    1
  )                                       AS porcentaje
FROM lineas_ticket l
JOIN tickets t ON l.ticket_hash = t.ticket_hash
WHERE l.categoria IS NOT NULL
GROUP BY t.user_id, l.categoria
ORDER BY t.user_id, total_gasto DESC;

-- -----------------------------------------------------------
-- 7. VISTA: resumen_subcategorias
-- -----------------------------------------------------------
CREATE OR REPLACE VIEW resumen_subcategorias AS
SELECT
  t.user_id,
  l.subcategoria,
  l.categoria,
  ROUND(SUM(l.precio_total)::numeric, 2) AS total_gasto,
  COUNT(*)                                AS num_productos
FROM lineas_ticket l
JOIN tickets t ON l.ticket_hash = t.ticket_hash
WHERE l.subcategoria IS NOT NULL
GROUP BY t.user_id, l.subcategoria, l.categoria
ORDER BY t.user_id, total_gasto DESC;

-- -----------------------------------------------------------
-- 8. VISTA: top_productos
-- -----------------------------------------------------------
CREATE OR REPLACE VIEW top_productos AS
SELECT
  t.user_id,
  l.nombre_normalizado,
  ROUND(SUM(l.precio_total)::numeric, 2) AS total_gasto,
  COUNT(DISTINCT l.ticket_hash)           AS veces_comprado,
  ROUND(AVG(l.precio_unitario)::numeric, 2) AS precio_medio
FROM lineas_ticket l
JOIN tickets t ON l.ticket_hash = t.ticket_hash
GROUP BY t.user_id, l.nombre_normalizado
ORDER BY t.user_id, total_gasto DESC;

-- -----------------------------------------------------------
-- 9. FUNCIÓN: auto‑update updated_at
-- -----------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

DROP TRIGGER IF EXISTS trg_tickets_updated_at ON tickets;
CREATE TRIGGER trg_tickets_updated_at
  BEFORE UPDATE ON tickets
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
