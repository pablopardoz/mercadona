from flask import Blueprint, jsonify, g
from database import get_dashboard_data
from decorators import jwt_required

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


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
def dashboard():
    data = get_dashboard_data(g.user_id)

    kpis = {
        'producto_mas_caro': _serialize_one(
            data['kpis']['producto_mas_caro'],
            ['nombre_normalizado', 'precio_unitario', 'supermercado', 'fecha'],
        ),
        'producto_mas_comprado': _serialize_one(
            data['kpis']['producto_mas_comprado'],
            ['nombre_normalizado', 'total_cantidad', 'veces'],
        ),
        'producto_mas_frecuente': _serialize_one(
            data['kpis']['producto_mas_frecuente'],
            ['nombre_normalizado', 'veces', 'total_cantidad'],
        ),
        'producto_mas_variable': _serialize_one(
            data['kpis']['producto_mas_variable'],
            ['nombre_normalizado', 'precio_min', 'precio_max', 'diff', 'veces'],
        ),
        'super_mas_visitado': _serialize_one(
            data['kpis']['super_mas_visitado'],
            ['supermercado', 'veces', 'total'],
        ),
        'top_productos': _serialize(
            data['kpis']['top_productos'],
            ['nombre_normalizado', 'total_gasto', 'veces'],
        ),
    }

    totals = {
        'resumen': _serialize_one(
            data['totals']['resumen'],
            ['num_tickets', 'total_global'],
        ),
        'por_mes': _serialize(
            data['totals']['por_mes'],
            ['mes', 'total', 'num_tickets'],
        ),
        'por_anio': _serialize(
            data['totals']['por_anio'],
            ['anio', 'total', 'num_tickets'],
        ),
    }

    categories = {
        'por_categoria': _serialize(
            data['categories']['por_categoria'],
            ['categoria', 'total', 'num_productos'],
        ),
        'por_subcategoria': _serialize(
            data['categories']['por_subcategoria'],
            ['subcategoria', 'categoria', 'total', 'num_productos'],
        ),
    }

    tickets = []
    for t in data['tickets']:
        ticket = dict(zip(TICKET_COLS, t))
        ticket['lineas'] = []
        if ticket['ticket_hash'] in data['lineas_por_ticket']:
            ticket['lineas'] = _serialize(
                data['lineas_por_ticket'][ticket['ticket_hash']],
                LINEA_COLS,
            )
        tickets.append(ticket)

    return jsonify({
        'kpis': kpis,
        'totals': totals,
        'categories': categories,
        'tickets': tickets,
    })
