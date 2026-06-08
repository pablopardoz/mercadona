from flask import Blueprint, jsonify
from database import get_supermarkets

bp = Blueprint('supermarkets', __name__, url_prefix='/api/supermarkets')


def _serialize(rows, columns):
    return [dict(zip(columns, r)) for r in rows]


SUPERMARKET_COLS = ['id', 'nombre', 'direccion', 'coordenadas']


@bp.route('/', methods=['GET'])
def list_supermarkets():
    rows = get_supermarkets()
    return jsonify({'supermarkets': _serialize(rows, SUPERMARKET_COLS)})
