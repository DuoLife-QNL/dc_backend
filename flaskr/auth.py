from flask import (
    Blueprint, jsonify, request, Flask
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='{}')".format(self.id)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    db = get_db()
    return_dict = {}
    return_dict['result'] = 'Succeeded'

    # 在前端将username 和 password 设置为必填字段，后端不做此判断
    if db.execute(
        '''
        SELECT id 
        FROM user 
        WHERE username = ?
        ''', (username,)
    ).fetchone() is not None:
        return_dict['result'] = 'Failed'
        return_dict['message'] = 'User {} is already registered.'.format(username)

    if return_dict['result'] == 'Succeeded':
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()

    return jsonify(return_dict)

def authenticate(username, password):
    db = get_db()
    user_db = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    user = User(user_db['id'], user_db['username'], user_db['password'])
    if check_password_hash(user.password, password):
        return user

def identity(payload):
    user_id = payload['identity']
    db = get_db()
    user_db = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    user = User(user_db['id'], user_db['username'], user_db['password'])
    return user
