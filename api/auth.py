from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta, timezone
import jwt
from werkzeug.security import check_password_hash
from config import Config
from database import get_user_by_username, get_user_by_id, create_user, update_user
from decorators import jwt_required

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _make_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user[0],
        'username': user[1],
        'iat': now,
        'exp': now + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Cuerpo JSON requerido'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400

    user = get_user_by_username(username)
    if not user or not check_password_hash(user[2], password):
        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

    token = _make_token(user)
    return jsonify({
        'token': token,
        'user': {'id': user[0], 'username': user[1]},
    })


@bp.route('/register', methods=['POST'])
@jwt_required
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Cuerpo JSON requerido'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    if len(password) < 3:
        return jsonify({'error': 'La contraseña debe tener al menos 3 caracteres'}), 400

    user = create_user(username, password)
    if not user:
        return jsonify({'error': 'El usuario ya existe'}), 409

    return jsonify({'message': 'Usuario creado', 'user': {'id': user[0], 'username': user[1]}}), 201


@bp.route('/user', methods=['PUT'])
@jwt_required
def modify_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Cuerpo JSON requerido'}), 400

    new_username = data.get('username', '').strip()
    new_password = data.get('password', '')

    user = update_user(
        g.user_id,
        username=new_username if new_username else None,
        password=new_password if new_password else None,
    )

    return jsonify({'message': 'Usuario actualizado', 'user': {'id': user[0], 'username': user[1]}})


@bp.route('/me', methods=['GET'])
@jwt_required
def me():
    user = get_user_by_id(g.user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({
        'user': {
            'id': user[0],
            'username': user[1],
            'created_at': str(user[3]),
        }
    })


@bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    return jsonify({'message': 'Sesión cerrada'})
