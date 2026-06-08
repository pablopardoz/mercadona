from flask import Blueprint, request, jsonify, g
from database import get_tickets, get_ticket_detail, create_ticket, delete_ticket
from decorators import jwt_required

bp = Blueprint('tickets', __name__, url_prefix='/api/tickets')


def _serialize(rows, columns):
    return [dict(zip(columns, r)) for r in rows]


def _serialize_one(row, columns):
    if not row:
        return None
    return dict(zip(columns, row))


TICKET_COLS = ['ticket_hash', 'supermercado', 'fecha', 'hora', 'total_gasto', 'created_at']
LINEA_COLS = ['id', 'nombre_normalizado', 'cantidad', 'precio_unitario',
              'precio_total', 'categoria', 'subcategoria']


@bp.route('/', methods=['GET'])
@jwt_required
def list_tickets():
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    rows = get_tickets(g.user_id, limit=limit, offset=offset)
    return jsonify({'tickets': _serialize(rows, TICKET_COLS)})


@bp.route('/<ticket_hash>', methods=['GET'])
@jwt_required
def detail(ticket_hash):
    result = get_ticket_detail(ticket_hash, g.user_id)
    if not result:
        return jsonify({'error': 'Ticket no encontrado'}), 404
    ticket = _serialize_one(result['ticket'], TICKET_COLS)
    lineas = _serialize(result['lineas'], LINEA_COLS)
    return jsonify({'ticket': ticket, 'lineas': lineas})


@bp.route('/', methods=['POST'])
@jwt_required
def new_ticket():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Cuerpo JSON requerido'}), 400

    supermercado = data.get('supermercado', '').strip()
    fecha = data.get('fecha', '').strip()
    hora = data.get('hora', '').strip()
    total_gasto = float(data['total_gasto']) if 'total_gasto' in data else None
    lineas = data.get('lineas', [])

    if not supermercado or not fecha:
        return jsonify({'error': 'supermercado y fecha son requeridos'}), 400
    if not lineas:
        return jsonify({'error': 'Se requiere al menos una línea'}), 400

    ticket_hash = create_ticket(
        g.user_id, supermercado, fecha, hora, total_gasto, lineas
    )
    return jsonify({'message': 'Ticket creado', 'ticket_hash': ticket_hash}), 201


@bp.route('/<ticket_hash>', methods=['DELETE'])
@jwt_required
def remove(ticket_hash):
    ok = delete_ticket(ticket_hash, g.user_id)
    if not ok:
        return jsonify({'error': 'Ticket no encontrado'}), 404
    return jsonify({'message': 'Ticket eliminado'})
