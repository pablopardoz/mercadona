from flask import Blueprint, jsonify, g
from database import get_totals, get_categorias
from decorators import jwt_required

bp = Blueprint('stats', __name__, url_prefix='/api/stats')


def _serialize(rows, columns):
    return [dict(zip(columns, r)) for r in rows]


def _serialize_one(row, columns):
    if not row:
        return None
    return dict(zip(columns, row))


@bp.route('/totals', methods=['GET'])
@jwt_required
def totals():
    data = get_totals(g.user_id)
    resumen = _serialize_one(data['resumen'], ['num_tickets', 'total_global'])
    por_mes = _serialize(data['por_mes'], ['mes', 'total', 'num_tickets'])
    por_anio = _serialize(data['por_anio'], ['anio', 'total', 'num_tickets'])
    return jsonify({'resumen': resumen, 'por_mes': por_mes, 'por_anio': por_anio})


@bp.route('/categories', methods=['GET'])
@jwt_required
def categories():
    data = get_categorias(g.user_id)
    por_categoria = _serialize(data['por_categoria'],
                               ['categoria', 'total', 'num_productos'])
    por_subcategoria = _serialize(data['por_subcategoria'],
                                  ['subcategoria', 'categoria', 'total', 'num_productos'])
    return jsonify({'por_categoria': por_categoria, 'por_subcategoria': por_subcategoria})
