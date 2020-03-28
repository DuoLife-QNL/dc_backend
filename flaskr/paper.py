from flask import (
    Blueprint, request, current_app, jsonify
)

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

import base64, os

from backend_model.net import Model

model = Model()

bp = Blueprint('paper', __name__, url_prefix='/paper')

# 由于flaskr是一个模块，程序运行时是在flaskr的外层目录下运行的
STORAGE_FOLDER = './storage'

@bp.route('/upload/img', methods=['POST'])
@jwt_required
def upload_img():
    # 获取传输的base64格式数据
    # 使用axios传送json数据，使用get_json方法
    data = request.get_json(silent=True)
    img_base64 = data['imageData']
    bookNo = data['bookNo']
    paperNo = data['paperNo']

    # 去除base64传送来的头，只保留有效内容
    img_base64 = img_base64.split(',')[1]
    img_jpg = base64.b64decode(img_base64)
    
    # 将图片一并保存
    current_user = get_jwt_identity()
    if current_user is not None:
        filename = str(current_user) + '-temp.jpg'
    else:
        filename = 'temp.jpg'
    dir_name = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    filename = os.path.join(dir_name, filename)
    
    file = open(filename, 'wb')
    file.write(img_jpg)
    file.close()

    letters = model.getAns(filename, 0.5)
    dict = {}
    dict['letters'] = []
    for (index, item) in  enumerate(letters):
        letter = {
            'no': index + 1,
            'class': item.classn,
            'box': item.boxesn,
            'score': item.scoren
        }
        dict['letters'].append(letter)
    if (len(letters) == 40):
        dict['valid'] = True
    else:
        dict['valid'] = False   
    return jsonify(dict)