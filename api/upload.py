import json
import hashlib
import logging
from flask import Blueprint, request, jsonify, g
from decorators import jwt_required
from database import create_ticket_with_hash, get_ticket_detail
from config import Config

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

CATEGORIAS_VALIDAS = [
    "Lácteos y Huevos", "Carnicería y Aves", "Pescadería", "Frutas y Verduras",
    "Despensa y Ultramarinos", "Panadería y Pastelería", "Bebidas",
    "Limpieza y Hogar", "Cuidado Personal y Perfumería", "Mascotas", "Otros",
]

PROMPT_IA = f"""
Analiza este ticket de supermercado y extrae la información estructurada.

REGLAS CRÍTICAS DE NORMALIZACIÓN:
1. El JSON debe tener: supermercado, fecha (YYYY-MM-DD), hora (HH:MM), total_gasto, productos[]
2. Cada producto debe tener: nombre_normalizado, cantidad, precio_unitario, precio_total, categoria, subcategoria
3. Categorías válidas: {CATEGORIAS_VALIDAS}
4. 'LECHE ENT. PASC' -> categoría 'Lácteos y Huevos', subcategoría 'Leche'
5. 'P. POLLO FIS.' -> 'Pechuga de pollo fileteada'
6. Si viene en peso (0,450 kg x 6,00€/kg), extrae cantidad=0.450 y precio_unitario=6.00
"""


@bp.route('/', methods=['POST'])
@jwt_required
def upload_ticket():
    import time
    _start = time.time()
    logging.info("POST /api/upload/ — inicio de procesamiento")

    if 'file' not in request.files:
        logging.warning("No se recibió campo 'file' en la petición")
        return jsonify({'error': 'Se requiere un archivo PDF en el campo "file"'}), 400

    file = request.files['file']
    if file.filename == '':
        logging.warning("El archivo recibido tiene nombre vacío")
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if not file.filename.lower().endswith('.pdf'):
        logging.warning("El archivo '%s' no es PDF", file.filename)
        return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

    pdf_bytes = file.read()
    file_hash = hashlib.md5(pdf_bytes).hexdigest()
    logging.info("Archivo recibido: %s (%d bytes, hash: %s)", file.filename, len(pdf_bytes), file_hash)

    detail = get_ticket_detail(file_hash, g.user_id)
    if detail:
        return jsonify({
            'message': 'Ticket ya procesado',
            'ticket_hash': file_hash,
            'ticket': detail,
        })

    if not Config.GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY no configurada")
        return jsonify({'error': 'GEMINI_API_KEY no configurada. Crea un .env con GEMINI_API_KEY=...'}), 500

    MODELS_FALLBACK = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    GEMINI_TIMEOUT = 60

    logging.info("Iniciando procesamiento con Gemini (PDF hash: %s, tamaño: %d bytes)", file_hash, len(pdf_bytes))

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    last_error = None
    ticket_data = None

    for model_name in MODELS_FALLBACK:
        logging.info("Intentando modelo: %s (timeout=%ds)", model_name, GEMINI_TIMEOUT)
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                    PROMPT_IA,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
                timeout=GEMINI_TIMEOUT,
            )
            logging.info("Respuesta recibida de %s", model_name)
            ticket_data = json.loads(response.text)
            logging.info("JSON parseado correctamente: %d productos", len(ticket_data.get('productos', [])))
            if ticket_data:
                break
        except json.JSONDecodeError as e:
            last_error = e
            logging.error("JSON inválido de %s: %s. Texto: %.200s", model_name, e, getattr(response, 'text', 'N/A'))
        except Exception as e:
            last_error = e
            logging.warning("Modelo %s falló: %s", model_name, e)

    if ticket_data is None:
        logging.error("Todos los modelos fallaron. Último error: %s", last_error)
        return jsonify({'error': f'Error al procesar el PDF con IA. Intentados: {MODELS_FALLBACK}. Último error: {last_error}'}), 500

    logging.info("Ticket procesado: %s productos, supermercado=%s, total=%s (%.1fs)",
                 len(ticket_data.get('productos', [])),
                 ticket_data.get('supermercado'),
                 ticket_data.get('total_gasto'),
                 time.time() - _start)

    lineas = []
    for p in ticket_data.get('productos', []):
        lineas.append({
            'nombre_normalizado': p.get('nombre_normalizado', ''),
            'cantidad': p.get('cantidad', 1),
            'precio_unitario': p['precio_unitario'],
            'precio_total': p.get('precio_total', p['precio_unitario'] * p.get('cantidad', 1)),
            'categoria': p.get('categoria', ''),
            'subcategoria': p.get('subcategoria', ''),
        })

    create_ticket_with_hash(
        file_hash,
        g.user_id,
        ticket_data.get('supermercado', ''),
        ticket_data.get('fecha', ''),
        ticket_data.get('hora', ''),
        ticket_data.get('total_gasto'),
        lineas,
    )

    elapsed = time.time() - _start
    logging.info("POST /api/upload/ — completado en %.1fs (hash: %s)", elapsed, file_hash)

    return jsonify({
        'message': 'Ticket procesado y almacenado',
        'ticket_hash': file_hash,
        'ticket': ticket_data,
    }), 201
