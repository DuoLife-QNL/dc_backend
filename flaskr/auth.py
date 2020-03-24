from flask import (
    Blueprint, jsonify, request
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
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

