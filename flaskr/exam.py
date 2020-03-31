from flask import (
    Blueprint, request, jsonify
)

from flask_jwt_extended import(
    jwt_required, get_jwt_identity
)

from flaskr.db import get_db

bp = Blueprint('exam', __name__, url_prefix='/exam')

@bp.route('/create', methods = ['POST'])
@jwt_required
def create():
    name = request.json.get('name')
    description = request.json.get('description', None)
    std_answer = request.json.get('std_answer')

    db = get_db()
    sql_create_exam = """
    --sql
    INSERT INTO exam(name, description)
    VALUES(?,?) 
    ;
    """
    sql_user_exam = """
    --sql
    INSERT INTO user_exam(user_id, exam_id)
    VALUES(?, ?) 
    ;
    """
    sql_get_exam = """
    --sql
    SELECT * 
    FROM exam
    WHERE name=(?)
    ;
    """
    sql_std_answer = """
    --sql
    INSERT INTO std_answer(exam_id, problem_no, problem_score, content)
    VALUES(?,?,?,?)
    ;
    """

    if db.execute(sql_get_exam, (name,)).fetchone() is None:
        # 创建考试，加入考试表
        db.execute(sql_create_exam, (name, description))
        exam = db.execute(sql_get_exam, (name,)).fetchone()

        # 插入用户-考试表，使当前用户与这场考试相关联
        # 此时current_user为已登录用户的id，数据类型为integer
        current_user = get_jwt_identity()
        db.execute(sql_user_exam, (current_user, exam['id']))

        for (i, data) in enumerate(std_answer, 1):
            content = str(data)[0]
            problem_score = int(str(data)[1])

            db.execute(sql_std_answer, (exam['id'], i, problem_score, content))

        db.commit()

        return jsonify(result='Succeeded', examID=exam['id'] + 100000)
    else:
        return jsonify(result='Failed', message='An exam of the same name already exists.')