from flask import (
    Blueprint, request, current_app
)

import base64, os

bp = Blueprint('upload', __name__, url_prefix='/upload')

# 由于flaskr是一个模块，程序运行时是在flaskr的外层目录下运行的
STORAGE_FOLDER = './storage'

@bp.route('/img', methods=['POST'])
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
    filename = str(bookNo) + '_' + str(paperNo) + '.jpg'
    dir_name = os.path.join(current_app.config['UPLOAD_FOLDER'], str(bookNo))
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    filename = os.path.join(dir_name, filename)
    
    file = open(filename, 'wb')
    file.write(img_jpg)
    file.close()

    # letters = model.getAns(filename, 0.5)
    # dict = {}
    # dict['letters'] = []
    # for (index, item) in  enumerate(letters):
    #     letter = {
    #         'no': index + 1,
    #         'class': item.classn,
    #         'box': item.boxesn,
    #         'score': item.scoren
    #     }
    #     dict['letters'].append(letter)
    # if (len(letters) == 40):
    #     dict['valid'] = True
    # else:
    #     dict['valid'] = False   
    # return jsonify(dict)
    return 'done'