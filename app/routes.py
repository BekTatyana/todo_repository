from flask import jsonify, request, g
from app import app, db
from pydantic import ValidationError
from app.utils.html_text import html_text
from app.utils.xlsx_and_csv import xlsx_csv
from app.pydantic_file import AddTask, IdDel, NameDel, LoginPassword
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(login, password):
    LoginPassword.model_validate({"login": login, "password": password})
    super_key = request.headers.get('X-Key')
    result = db.auth_user(login, password, super_key)
    if result:
        g.user = login
    return result

#обработка ошибки auth
@auth.error_handler
def auth_error(status):
    return jsonify({"error": "Требуется аутентификация"}), status

#главная страница
@app.route('/', methods=['GET'])
def main_page():
    return html_text


# Добавление задач
@app.route('/api/tasks', methods=['POST'])
@auth.login_required
def add_tasks():
    try:
        
        AddTask.model_validate(request.json)
        data = request.get_json()
        username = data['username']
        tasks = data['tasks']
    
        result_save = db.save_tasks(username, tasks,g.user)

        xlsxcsv = xlsx_csv(db.get_all_info(g.user))
        result_csv = xlsxcsv.add_to_csv()
        result_xlsx = xlsxcsv.add_to_xlsx()
        
        result_for_all = {
            "Database": result_save,
            "Csv ": result_csv,
            "Xlsx": result_xlsx
            }

        return jsonify(result_for_all), 201
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 500

# Получение всех задач
@app.route('/api/tasks', methods=['GET'])
@auth.login_required
def get_all_tasks():

    try:
        full_info = db.get_all_info(g.user)
        return jsonify(full_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Удаление задачи по ID
@app.route('/api/tasks/id', methods=['DELETE'])
@auth.login_required
def delete_id_tasks():

    try:
        IdDel.model_validate(request.json)

        task_id = request.get_json()
        success = db.delete_only_id_tasks(list(task_id["id"]),g.user)
        if not success:
            return jsonify({"error": "При удалении задач произошла ошибка"}), 404

        return jsonify({"Успех": success}), 201
         
    except ValidationError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/name',methods = ['DELETE'])
@auth.login_required
def delete_name():
    try:
        NameDel.model_validate(request.json)
        name_info = request.get_json()
        
        success = db.delete_user_tasks(name_info["username"],g.user)

        if not success:
            return jsonify({"error": "При удалении задач произошла ошибка"}), 404
            
        return jsonify({"success": success}), 201
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 500          

@app.route('/api/tasks/all',methods = ['DELETE'])
@auth.login_required
def delete_all():
    success = db.delete_all(g.user)
    if not success:
            return jsonify({"error": "При удалении задач произошла ошибка"}), 404
    return jsonify({"success": success}), 201
