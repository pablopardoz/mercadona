import os
import hashlib
import time
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import DictCursor
from werkzeug.security import generate_password_hash
from config import Config

_pool = None
_db_initialized = False


def init_pool():
    global _pool, _db_initialized
    if _pool is None:
        print("DB URL:", Config.SUPABASE_DB_URL)
        _pool = SimpleConnectionPool(1, 10, Config.SUPABASE_DB_URL, sslmode='require')
    if not _db_initialized:
        conn = _pool.getconn()
        try:
            _init_db(conn)
            _db_initialized = True
        finally:
            _pool.putconn(conn)


def get_conn():
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
    except (psycopg2.InterfaceError, psycopg2.OperationalError):
        print("Reconectando a la base de datos...")
        close_pool()
        init_pool()
        conn = _pool.getconn()
    return conn


def put_conn(conn):
    _pool.putconn(conn)


def close_pool():
    global _pool, _db_initialized
    if _pool:
        _pool.closeall()
        _pool = None
        _db_initialized = False


def _init_db(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_hash VARCHAR PRIMARY KEY,
            supermercado VARCHAR,
            fecha DATE,
            hora VARCHAR,
            total_gasto NUMERIC(10,2),
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lineas_ticket (
            id SERIAL PRIMARY KEY,
            ticket_hash VARCHAR REFERENCES tickets(ticket_hash) ON DELETE CASCADE,
            nombre_normalizado VARCHAR,
            cantidad NUMERIC(10,3) DEFAULT 1,
            precio_unitario NUMERIC(10,2) DEFAULT 0,
            precio_total NUMERIC(10,2) DEFAULT 0,
            categoria VARCHAR,
            subcategoria VARCHAR
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS supermarkets (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre VARCHAR NOT NULL,
            direccion VARCHAR DEFAULT NULL,
            coordenadas VARCHAR DEFAULT NULL
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_lineas_ticket_hash ON lineas_ticket (ticket_hash)
    """)
    conn.commit()
    cur.close()
    _seed_default_user(conn)


def _seed_default_user(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    exists = cur.fetchone()[0]
    if exists == 0:
        pw_hash = generate_password_hash('pablo')
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            ['pablo', pw_hash],
        )
        conn.commit()
    cur.close()


def _next_id(table, conn=None):
    close_conn = False
    if conn is None:
        conn = get_conn()
        close_conn = True
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table}")
        return cur.fetchone()[0]
    finally:
        cur.close()
        if close_conn:
            put_conn(conn)


def _next_ticket_hash():
    raw = f"{time.time()}{os.urandom(8).hex()}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ── User queries ────────────────────────────────────────────

def get_user_by_username(username):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash, created_at, updated_at FROM users WHERE username = %s",
            [username],
        )
        return cur.fetchone()
    finally:
        cur.close()
        put_conn(conn)


def get_user_by_id(user_id):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash, created_at, updated_at FROM users WHERE id = %s",
            [user_id],
        )
        return cur.fetchone()
    finally:
        cur.close()
        put_conn(conn)


def create_user(username, password):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", [username])
        exists = cur.fetchone()[0]
        if exists:
            return None
        pw_hash = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id, username, password_hash, created_at, updated_at",
            [username, pw_hash],
        )
        conn.commit()
        return cur.fetchone()
    finally:
        cur.close()
        put_conn(conn)


def update_user(user_id, username=None, password=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        if username:
            cur.execute(
                "UPDATE users SET username = %s, updated_at = NOW() WHERE id = %s",
                [username, user_id],
            )
        if password:
            pw_hash = generate_password_hash(password)
            cur.execute(
                "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s",
                [pw_hash, user_id],
            )
        conn.commit()
        cur.close()
        return get_user_by_id(user_id)
    finally:
        put_conn(conn)


# ── Ticket queries ──────────────────────────────────────────

def get_tickets(user_id, limit=100, offset=0):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT ticket_hash, supermercado, fecha, hora, total_gasto, created_at
               FROM tickets WHERE user_id = %s
               ORDER BY fecha DESC, hora DESC
               LIMIT %s OFFSET %s""",
            [user_id, limit, offset],
        )
        return cur.fetchall()
    finally:
        cur.close()
        put_conn(conn)


def get_ticket_detail(ticket_hash, user_id):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT ticket_hash, supermercado, fecha, hora, total_gasto, created_at
               FROM tickets WHERE ticket_hash = %s AND user_id = %s""",
            [ticket_hash, user_id],
        )
        ticket = cur.fetchone()
        if not ticket:
            return None
        cur.execute(
            """SELECT id, nombre_normalizado, cantidad, precio_unitario, precio_total,
                      categoria, subcategoria
               FROM lineas_ticket WHERE ticket_hash = %s
               ORDER BY categoria, subcategoria, nombre_normalizado""",
            [ticket_hash],
        )
        lineas = cur.fetchall()
        return {'ticket': ticket, 'lineas': lineas}
    finally:
        cur.close()
        put_conn(conn)


def create_ticket(user_id, supermercado, fecha, hora, total_gasto, lineas):
    conn = get_conn()
    try:
        cur = conn.cursor()
        ticket_hash = _next_ticket_hash()
        cur.execute(
            """INSERT INTO tickets (ticket_hash, supermercado, fecha, hora, total_gasto, user_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            [ticket_hash, supermercado, fecha, hora, total_gasto, user_id],
        )
        for linea in lineas:
            cur.execute(
                """INSERT INTO lineas_ticket (ticket_hash, nombre_normalizado, cantidad,
                                               precio_unitario, precio_total, categoria, subcategoria)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                [
                    ticket_hash,
                    linea['nombre_normalizado'],
                    linea.get('cantidad', 1),
                    linea['precio_unitario'],
                    linea.get('precio_total', linea['precio_unitario'] * linea.get('cantidad', 1)),
                    linea.get('categoria', ''),
                    linea.get('subcategoria', ''),
                ],
            )
        conn.commit()
        return ticket_hash
    finally:
        cur.close()
        put_conn(conn)


def create_ticket_with_hash(ticket_hash, user_id, supermercado, fecha, hora, total_gasto, lineas):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO tickets (ticket_hash, supermercado, fecha, hora, total_gasto, user_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            [ticket_hash, supermercado, fecha, hora, total_gasto, user_id],
        )
        for linea in lineas:
            cur.execute(
                """INSERT INTO lineas_ticket (ticket_hash, nombre_normalizado, cantidad,
                                               precio_unitario, precio_total, categoria, subcategoria)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                [
                    ticket_hash,
                    linea['nombre_normalizado'],
                    linea.get('cantidad', 1),
                    linea['precio_unitario'],
                    linea.get('precio_total', linea['precio_unitario'] * linea.get('cantidad', 1)),
                    linea.get('categoria', ''),
                    linea.get('subcategoria', ''),
                ],
            )
        conn.commit()
        return ticket_hash
    finally:
        cur.close()
        put_conn(conn)


def delete_ticket(ticket_hash, user_id):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM tickets WHERE ticket_hash = %s AND user_id = %s",
            [ticket_hash, user_id],
        )
        if not cur.fetchone():
            return False
        cur.execute("DELETE FROM lineas_ticket WHERE ticket_hash = %s", [ticket_hash])
        cur.execute("DELETE FROM tickets WHERE ticket_hash = %s", [ticket_hash])
        conn.commit()
        return True
    finally:
        cur.close()
        put_conn(conn)


# ── Stats queries ───────────────────────────────────────────

def get_totals(user_id):
    conn = get_conn()
    try:
        cur = conn.cursor()

        cur.execute(
            """SELECT COUNT(*) AS num_tickets, COALESCE(SUM(total_gasto), 0) AS total_global
               FROM tickets WHERE user_id = %s""",
            [user_id],
        )
        resumen = cur.fetchone()

        cur.execute(
            """SELECT TO_CHAR(fecha, 'YYYY-MM') AS mes,
                      SUM(total_gasto) AS total,
                      COUNT(*) AS num_tickets
               FROM tickets WHERE user_id = %s
               GROUP BY mes ORDER BY mes""",
            [user_id],
        )
        por_mes = cur.fetchall()

        cur.execute(
            """SELECT TO_CHAR(fecha, 'YYYY') AS anio,
                      SUM(total_gasto) AS total,
                      COUNT(*) AS num_tickets
               FROM tickets WHERE user_id = %s
               GROUP BY anio ORDER BY anio""",
            [user_id],
        )
        por_anio = cur.fetchall()

        return {'resumen': resumen, 'por_mes': por_mes, 'por_anio': por_anio}
    finally:
        cur.close()
        put_conn(conn)


def get_categorias(user_id):
    conn = get_conn()
    try:
        cur = conn.cursor()

        cur.execute(
            """SELECT l.categoria, SUM(l.precio_total) AS total, COUNT(*) AS num_productos
               FROM lineas_ticket l
               JOIN tickets t ON l.ticket_hash = t.ticket_hash
               WHERE t.user_id = %s
               GROUP BY l.categoria ORDER BY total DESC""",
            [user_id],
        )
        por_categoria = cur.fetchall()

        cur.execute(
            """SELECT l.subcategoria, l.categoria, SUM(l.precio_total) AS total, COUNT(*) AS num_productos
               FROM lineas_ticket l
               JOIN tickets t ON l.ticket_hash = t.ticket_hash
               WHERE t.user_id = %s
               GROUP BY l.subcategoria, l.categoria ORDER BY total DESC""",
            [user_id],
        )
        por_subcategoria = cur.fetchall()

        return {'por_categoria': por_categoria, 'por_subcategoria': por_subcategoria}
    finally:
        cur.close()
        put_conn(conn)


def get_kpis(user_id):
    conn = get_conn()
    try:
        cur = conn.cursor()
        data = {}

        cur.execute(
            """SELECT l.nombre_normalizado, l.precio_unitario, t.supermercado, t.fecha
               FROM lineas_ticket l
               JOIN tickets t ON l.ticket_hash = t.ticket_hash
               WHERE t.user_id = %s
               ORDER BY l.precio_unitario DESC LIMIT 1""",
            [user_id],
        )
        data['producto_mas_caro'] = cur.fetchone()

        cur.execute(
            """SELECT nombre_normalizado, SUM(cantidad) AS total_cantidad,
                      COUNT(DISTINCT l.ticket_hash) AS veces
               FROM lineas_ticket l
               JOIN tickets t ON l.ticket_hash = t.ticket_hash
               WHERE t.user_id = %s
               GROUP BY nombre_normalizado
               ORDER BY total_cantidad DESC LIMIT 1""",
            [user_id],
        )
        data['producto_mas_comprado'] = cur.fetchone()

        cur.execute(
            """SELECT nombre_normalizado, COUNT(DISTINCT l.ticket_hash) AS veces,
                      SUM(cantidad) AS total_cantidad
               FROM lineas_ticket l
               JOIN tickets t ON l.ticket_hash = t.ticket_hash
               WHERE t.user_id = %s
               GROUP BY nombre_normalizado
               ORDER BY veces DESC LIMIT 1""",
            [user_id],
        )
        data['producto_mas_frecuente'] = cur.fetchone()

        cur.execute(
            """SELECT nombre_normalizado,
                      MIN(precio_unitario) AS precio_min,
                      MAX(precio_unitario) AS precio_max,
                      MAX(precio_unitario) - MIN(precio_unitario) AS diff,
                      COUNT(DISTINCT l.ticket_hash) AS veces
               FROM lineas_ticket l
               JOIN tickets t ON l.ticket_hash = t.ticket_hash
               WHERE t.user_id = %s
               GROUP BY nombre_normalizado
               HAVING COUNT(DISTINCT l.ticket_hash) > 1 AND MAX(precio_unitario) > MIN(precio_unitario)
               ORDER BY diff DESC LIMIT 1""",
            [user_id],
        )
        data['producto_mas_variable'] = cur.fetchone()

        cur.execute(
            """SELECT supermercado, COUNT(*) AS veces, SUM(total_gasto) AS total
               FROM tickets WHERE user_id = %s
               GROUP BY supermercado ORDER BY veces DESC LIMIT 1""",
            [user_id],
        )
        data['super_mas_visitado'] = cur.fetchone()

        cur.execute(
            """SELECT l.nombre_normalizado, SUM(l.precio_total) AS total_gasto,
                      COUNT(DISTINCT l.ticket_hash) AS veces
               FROM lineas_ticket l
               JOIN tickets t ON l.ticket_hash = t.ticket_hash
               WHERE t.user_id = %s
               GROUP BY l.nombre_normalizado
               ORDER BY total_gasto DESC LIMIT 5""",
            [user_id],
        )
        data['top_productos'] = cur.fetchall()

        return data
    finally:
        cur.close()
        put_conn(conn)


# ── Supermarket queries ─────────────────────────────────────

def get_supermarkets():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, direccion, coordenadas FROM supermarkets ORDER BY nombre")
        return cur.fetchall()
    finally:
        cur.close()
        put_conn(conn)
