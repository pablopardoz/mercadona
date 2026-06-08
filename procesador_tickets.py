import os
import json
import hashlib
import duckdb
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Intentar importar la librería de Google GenAI o OpenAI.
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Por favor, instala el SDK oficial de Gemini: pip install google-genai pydantic")

# 1. Definición de la estructura de datos (Taxonomía fija para normalización)
CATEGORIAS_VALIDAS = [
    "Lácteos y Huevos", "Carnicería y Aves", "Pescadería", "Frutas y Verduras", 
    "Despensa y Ultramarinos", "Panadería y Pastelería", "Bebidas", 
    "Limpieza y Hogar", "Cuidado Personal y Perfumería", "Mascotas", "Otros"
]

class TicketItem(BaseModel):
    nombre_original: str = Field(description="El texto exacto del producto tal como viene en el ticket (ej: 'LECHE ENT. PASC.')")
    nombre_normalizado: str = Field(description="Nombre limpio, corregido y legible (ej: 'Leche entera Pascual')")
    cantidad: float = Field(description="Cantidad comprada (por unidades o kg)")
    precio_unitario: float = Field(description="Precio por unidad o por kilo")
    precio_total: float = Field(description="Precio total de esa línea (cantidad x precio_unitario)")
    categoria: str = Field(description=f"Debe ser estrictamente una de estas: {', '.join(CATEGORIAS_VALIDAS)}")
    subcategoria: str = Field(description="Subcategoría lógica (ej: Leche, Queso, Yogures, Pollo, Cerdo, Detergente, Agua, Refrescos, etc.)")

class TicketData(BaseModel):
    supermercado: str = Field(description="Nombre del supermercado (ej: Mercadona, Carrefour, Lidl, Dia)")
    fecha: Optional[str] = Field(description="Fecha de la compra en formato YYYY-MM-DD")
    hora: Optional[str] = Field(description="Hora de la compra en formato HH:MM")
    total_gasto: float = Field(description="El importe total pagado que figura al final del ticket")
    productos: List[TicketItem] = Field(description="Lista detallada de todos los productos del ticket")


# --- NUEVAS FUNCIONES DE BASE DE DATOS (DUCKDB) ---

def init_db(db_name="gastos.duckdb"):
    """Inicializa la base de datos DuckDB y crea las tablas si no existen."""
    conn = duckdb.connect(db_name)
    
    # Tabla principal del ticket
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_hash VARCHAR PRIMARY KEY,
            supermercado VARCHAR,
            fecha DATE,
            hora VARCHAR,
            total_gasto DOUBLE
        )
    """)
    
    # Tabla para los productos individuales de cada ticket
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lineas_ticket (
            ticket_hash VARCHAR,
            nombre_original VARCHAR,
            nombre_normalizado VARCHAR,
            cantidad DOUBLE,
            precio_unitario DOUBLE,
            precio_total DOUBLE,
            categoria VARCHAR,
            subcategoria VARCHAR,
            FOREIGN KEY (ticket_hash) REFERENCES tickets(ticket_hash)
        )
    """)
    return conn

def guardar_en_db(conn, ticket_data: dict, ticket_hash: str):
    """Guarda los datos del JSON en las tablas de DuckDB."""
    # Insertar la cabecera del ticket
    conn.execute("""
        INSERT INTO tickets (ticket_hash, supermercado, fecha, hora, total_gasto)
        VALUES (?, ?, CAST(? AS DATE), ?, ?)
    """, (
        ticket_hash,
        ticket_data.get("supermercado"),
        ticket_data.get("fecha"),
        ticket_data.get("hora"),
        ticket_data.get("total_gasto")
    ))
    
    # Insertar los productos (líneas del ticket)
    for item in ticket_data.get("productos", []):
        conn.execute("""
            INSERT INTO lineas_ticket (
                ticket_hash, nombre_original, nombre_normalizado, 
                cantidad, precio_unitario, precio_total, categoria, subcategoria
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_hash,
            item.get("nombre_original"),
            item.get("nombre_normalizado"),
            item.get("cantidad"),
            item.get("precio_unitario"),
            item.get("precio_total"),
            item.get("categoria"),
            item.get("subcategoria")
        ))
    conn.commit()

# --- FIN FUNCIONES DE BASE DE DATOS ---


def procesar_ticket_pdf(ruta_pdf: str, api_key: str = None) -> Optional[dict]:
    """
    Lee un archivo PDF de un ticket, lo envía a Gemini usando Structured Outputs 
    para garantizar la extracción y normalización en formato JSON según el esquema Pydantic.
    """
    client = genai.Client(api_key=api_key or os.environ.get("GEMINI_API_KEY"))
    
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"No se encontró el archivo PDF en la ruta: {ruta_pdf}")
    
    print(f"Cargando archivo PDF: {ruta_pdf}...")
    with open(ruta_pdf, "rb") as f:
        pdf_bytes = f.read()

    prompt_instrucciones = f"""
    Analiza este ticket de supermercado y extrae la información estructurada.
    
    REGLAS CRÍTICAS DE NORMALIZACIÓN:
    1. Categorías: Debes clasificar CADA producto única y exclusivamente en una de estas categorías: {CATEGORIAS_VALIDAS}.
    2. Agrupación inteligente: Si el producto es 'LECHE ENT. PASC', 'LECH NTERA', 'LECHE SEMI', etc., su categoría DEBE ser 'Lácteos y Huevos' y su subcategoría 'Leche'.
    3. Corrección de nombres: Transforma las abreviaturas confusas del ticket en nombres legibles en 'nombre_normalizado' (ej: 'P. POLLO FIS.' -> 'Pechuga de pollo fileteada').
    4. Cantidades: Si viene expresado en peso (ej: 0,450 kg x 6,00€/kg), extrae la cantidad (0.450) y el precio unitario (6.00).
    5. Asegúrate de que la suma de los precios de los productos coincida lógicamente con el 'total_gasto'.
    """

    print("Enviando documento a la IA para extracción y clasificación estructurada...")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type='application/pdf',
                ),
                prompt_instrucciones
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TicketData,
                temperature=0.1
            ),
        )
        
        resultado_json = json.loads(response.text)
        return resultado_json

    except Exception as e:
        print(f"Ocurrió un error al procesar con la IA: {e}")
        return None

if __name__ == "__main__":
    # La API KEY ahora se lee de forma segura desde el archivo .env
    MI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # Ruta del ticket de prueba (Cámbiala por tu archivo real)
    RUTA_TICKET = "/Users/ppardo/data_projects/mercadona/data/20260603 Mercadona 84,98 €.pdf"
    
    if not MI_API_KEY:
        print("[ERROR]: No se encontró GEMINI_API_KEY en el archivo .env")
    else:
        try:
            if not os.path.exists(RUTA_TICKET):
                print(f"Error: No se encontró el archivo inicial: {RUTA_TICKET}")
            else:
                # 1. HASHEAR EL ARCHIVO (MD5)
                hasher = hashlib.md5()
                with open(RUTA_TICKET, "rb") as f:
                    hasher.update(f.read())
                hash_archivo = hasher.hexdigest()
                
                # 2. DEFINIR NUEVOS NOMBRES BASADOS EN EL HASH
                directorio = os.path.dirname(RUTA_TICKET) or "."
                nuevo_nombre_pdf = os.path.join(directorio, f"ticket_{hash_archivo}.pdf")
                nombre_salida_json = os.path.join(directorio, f"ticket_{hash_archivo}.json")
                
                # 3. INICIALIZAR BASE DE DATOS DUCKDB
                conn = init_db("gastos.duckdb")
                
                # 4. COMPROBAR SI YA EXISTE EN LA BASE DE DATOS O LOCAL (EVITA DUPLICADOS)
                # Buscamos si el hash ya existe en la tabla tickets
                existe_db = conn.execute("SELECT 1 FROM tickets WHERE ticket_hash = ?", (hash_archivo,)).fetchone()
                
                if os.path.exists(nombre_salida_json) or existe_db:
                    print(f"[AVISO] El ticket ya fue procesado previamente (Hash: {hash_archivo}).")
                    print("Se ha cancelado la llamada a la IA para evitar subidas duplicadas.")
                else:
                    # Renombramos el PDF original con su hash
                    if RUTA_TICKET != nuevo_nombre_pdf and not os.path.exists(nuevo_nombre_pdf):
                        os.rename(RUTA_TICKET, nuevo_nombre_pdf)
                        print(f"[INFO] Archivo renombrado a: {nuevo_nombre_pdf}")
                    
                    # Ejecutar el procesamiento sobre el archivo ya renombrado
                    ticket_estructurado = procesar_ticket_pdf(nuevo_nombre_pdf, api_key=MI_API_KEY)
                    
                    if ticket_estructurado:
                        print("\n--- TICKET PROCESADO CON ÉXITO ---")
                        # Imprimir el JSON por pantalla (opcional, para depurar)
                        print(json.dumps(ticket_estructurado, indent=2, ensure_ascii=False))
                        
                        # Guardar en local el JSON
                        with open(nombre_salida_json, "w", encoding="utf-8") as f_out:
                            json.dump(ticket_estructurado, f_out, indent=2, ensure_ascii=False)
                        print(f"\n[INFO] Datos guardados localmente en: {nombre_salida_json}")
                        
                        # GUARDAR EN BASE DE DATOS DUCKDB
                        guardar_en_db(conn, ticket_estructurado, hash_archivo)
                        print(f"[INFO] Datos insertados correctamente en la base de datos DuckDB ('gastos.duckdb')")
                
                # Cerrar la conexión a la BD
                conn.close()
                        
        except Exception as e:
            print(f"Error en la ejecución: {e}")