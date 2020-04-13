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

@bp.route('/modify', methods=['POST'])
@jwt_required
def modify():
    id = request.json.get('id') - 100000
    name = request.json.get('name', None)
    description = request.json.get('description', None)
    std_answer = request.json.get('std_answer', None)

    sql_modify_name = """
    --sql
    UPDATE exam
    SET name=?
    WHERE id=?
    ;
    """
    sql_modify_description = """
    --sql
    UPDATE exam
    SET description=?
    WHERE id=?
    ;
    """
    sql_modify_std_answer = """
    --sql
    UPDATE std_answer
    SET content=?, problem_score=?
    WHERE exam_id=? AND problem_no=? 
    ;
    """
    sql_get_std_answer = """
    --sql
    SELECT *
    FROM std_answer
    WHERE problem_no = ?
    ;
    """
    sql_insert_std_answer = """
    --sql
    INSERT INTO std_answer(exam_id, problem_no, problem_score, content)
    VALUES(?,?,?,?)
    ;
    """

    db = get_db()
    if name is not None:
        db.execute(sql_modify_name, (name, id))
    if description is not None:
        db.execute(sql_modify_description, (description, id))
    if std_answer is not None:
        for problem in std_answer:
            if db.execute(sql_get_std_answer, (problem['problem_no'], )).fetchone() is not None:
                db.execute(sql_modify_std_answer, (problem['content'], problem['problem_score'], id, problem['problem_no']))
            else:
                db.execute(sql_insert_std_answer, (id, problem['problem_no'], problem['problem_score'], problem['content']))
    db.commit()

    return jsonify(result='Succeeded')        

@bp.route('/get-exam-info', methods=['POST'])
@jwt_required
def get_exam_info():
    id = request.json.get('id') - 100000

    sql_get_exam = """
    --sql
    SELECT *
    FROM exam
    WHERE id=? 
    ;
    """
    sql_get_std_answer = """
    --sql
    SELECT *
    FROM std_answer
    WHERE exam_id=?
    ORDER BY problem_no ASC
    ;
    """
    sql_insert_user_exam = """
    --sql
    INSERT INTO user_exam(user_id, exam_id)
    VALUES(?, ?) 
    ;
    """
    sql_get_user_exam = """
    --sql
    SELECT *
    FROM user_exam
    WHERE user_id=? AND exam_id=?
    ;
    """

    db = get_db()
    current_user = get_jwt_identity()
    if db.execute(sql_get_user_exam, (current_user, id)).fetchone() is None:
        db.execute(sql_insert_user_exam, (current_user, id))
        db.commit()

    exam = db.execute(sql_get_exam, (id,)).fetchone()
    if exam is None:
        return jsonify(result='Failed', message='The exam does not exist.')
    
    problems = db.execute(sql_get_std_answer, (id,))
    std_answer = []
    for problem in problems:
        std_answer.append(problem['content'] + str(problem['problem_score']))
    
    return_dict = {'id': id + 100000, 'name': exam['name'], 'description': exam['description'], 'std_answer': std_answer}
    return jsonify(return_dict)

@bp.route('/get-user-exam', methods=['GET'])
@jwt_required
def get_user_exam():
    db = get_db()
    current_user = get_jwt_identity()

    sql_get_info = """
    --sql
    SELECT *
    FROM exam
    where id IN (
        SELECT exam_id
        FROM user_exam
        WHERE user_id=?
    )
    ;
    """

    exam_info = db.execute(sql_get_info, (current_user,)).fetchall()
    
    if not len(exam_info):
        return jsonify(result='NULL', message='Current user has no exams.')
    else:
        info_dict_list = []
        for exam in exam_info:
            exam = dict(exam)
            exam['id'] = exam['id'] + 100000
            info_dict_list.append(exam)
        return jsonify(exam_info=info_dict_list)

@bp.route('/delete', methods=['POST'])
@jwt_required
def delete():
    id = request.json.get('examID') - 100000

    sql_delete = """
    --sql
    DELETE FROM exam
    WHERE id=?
    ;
    """
    sql_get_exam = """
    --sql
    SELECT * 
    FROM exam
    WHERE id=?
    ;
    """

    db = get_db()
    db.execute("PRAGMA foreign_keys = ON;")
    if db.execute(sql_get_exam, (id,)).fetchone() is None:
        return jsonify(result='Failed.', message='The exam does not exit.')
    db.execute(sql_delete, (id,))
    db.commit()
    return jsonify(result='Succeeded.')

@bp.route('/get-book-answer', methods=['POST'])
@jwt_required
def get_book_answer():
    exam_id = request.json.get('examID') - 100000
    book = request.json.get('book')

    sql_get_paper_id = """
    --sql
    SELECT *
    FROM paper
    WHERE exam_id=? AND book=?
    ORDER BY page ASC
    ;
    """
    sql_get_paper_answer = """
    --sql
    SELECT *
    FROM answer
    WHERE paper_id=?
    ORDER BY problem_no ASC
    ;
    """
    db = get_db()

    papers = db.execute(sql_get_paper_id, (exam_id, book)).fetchall()

    return_dict = {}
    for paper in papers:
        paper_id = paper['id']
        answers = db.execute(sql_get_paper_answer, (paper_id,)).fetchall()
        paper_list = []
        for answer in answers:
            paper_list.append(answer['content'])
        return_dict[paper['page']] = paper_list

    return(jsonify(return_dict))

@bp.route('/get-total-answer', methods=['POST'])
@jwt_required
def get_total_answer():
    exam_id = request.json.get('examID') - 100000

    sql_get_problem_sum = """
    --sql
    SELECT content, count(*) AS total_num
    FROM answer
    WHERE problem_no=? AND paper_id IN (
        SELECT id
        FROM paper
        WHERE exam_id=?
    )
    GROUP BY content
    ;
    """
    sql_get_total_problem_num = """
    --sql
    SELECT MAX(problem_no) AS problem_count
    FROM std_answer
    WHERE exam_id=?
    ;
    """

    db = get_db()
    return_dict = {}
    total_problem_no = db.execute(sql_get_total_problem_num, (exam_id,)).fetchone()['problem_count']
    for problem_no in range(1, total_problem_no + 1):
        problem_result = db.execute(sql_get_problem_sum, (problem_no, exam_id)).fetchall()
        problem_statistic_dict = {}
        for row in problem_result:
            problem_statistic_dict[row['content']] = row['total_num']
        return_dict[problem_no] = problem_statistic_dict    

    return(jsonify(return_dict))