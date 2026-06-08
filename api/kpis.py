from flask import Blueprint, jsonify, g
from database import get_kpis
from decorators import jwt_required

bp = Blueprint('kpis', __name__, url_prefix='/api/kpis')


def _serialize(rows, columns):
    return [dict(zip(columns, r)) for r in rows]


def _serialize_one(row, columns):
    if not row:
        return None
    return dict(zip(columns, row))


@bp.route('/', methods=['GET'])
@jwt_required
def kpis():
    data = get_kpis(g.user_id)

    resultado = {
        'producto_mas_caro': _serialize_one(
            data['producto_mas_caro'],
            ['nombre_normalizado', 'precio_unitario', 'supermercado', 'fecha'],
        ),
        'producto_mas_comprado': _serialize_one(
            data['producto_mas_comprado'],
            ['nombre_normalizado', 'total_cantidad', 'veces'],
        ),
        'producto_mas_frecuente': _serialize_one(
            data['producto_mas_frecuente'],
            ['nombre_normalizado', 'veces', 'total_cantidad'],
        ),
        'producto_mas_variable': _serialize_one(
            data['producto_mas_variable'],
            ['nombre_normalizado', 'precio_min', 'precio_max', 'diff', 'veces'],
        ),
        'super_mas_visitado': _serialize_one(
            data['super_mas_visitado'],
            ['supermercado', 'veces', 'total'],
        ),
        'top_productos': _serialize(
            data['top_productos'],
            ['nombre_normalizado', 'total_gasto', 'veces'],
        ),
    }

    return jsonify(resultado)
