import json
import hashlib
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
    if 'file' not in request.files:
        return jsonify({'error': 'Se requiere un archivo PDF en el campo "file"'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

    pdf_bytes = file.read()
    file_hash = hashlib.md5(pdf_bytes).hexdigest()

    detail = get_ticket_detail(file_hash, g.user_id)
    if detail:
        return jsonify({
            'message': 'Ticket ya procesado',
            'ticket_hash': file_hash,
            'ticket': detail,
        })

    if not Config.GEMINI_API_KEY:
        return jsonify({'error': 'GEMINI_API_KEY no configurada. Crea un .env con GEMINI_API_KEY=...'}), 500

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                PROMPT_IA,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        ticket_data = json.loads(response.text)

    except Exception as e:
        return jsonify({'error': f'Error al procesar el PDF con IA: {str(e)}'}), 500

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

    return jsonify({
        'message': 'Ticket procesado y almacenado',
        'ticket_hash': file_hash,
        'ticket': ticket_data,
    }), 201
