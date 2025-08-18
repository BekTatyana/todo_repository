from flask import jsonify, request
from app import app, db
from app.utils.split_lines import split_lines
from app.utils.html_text import html_text
from app.utils.xlsx_and_csv import xlsx_csv


@app.route('/', methods=['GET'])
def main_page():
    return html_text


# Добавление задач
@app.route('/api/tasks', methods=['POST'])
def add_tasks():
    
    data = request.get_json()
    
    if not data or 'username' not in data or 'tasks' not in data:
        return jsonify({"error": "Требуются поля: username и tasks"}), 400
    
    username = data['username'].strip().title()
    tasks = split_lines(data['tasks'])
    
    if not tasks:
        return jsonify({"error": "Список задач не может быть пустым"}), 400
    
    try:

        db.save_tasks(username, tasks)

        xlsxcsv = xlsx_csv(db.get_all_info())
        result_csv = xlsxcsv.add_to_csv()
        result_xlsx = xlsxcsv.add_to_xlsx()
        
        result_for_all = {
            "Database": "Задачи добавлены в БД",
            "Csv ": result_csv,
            "Xlsx": result_xlsx
            }

        return jsonify(result_for_all), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Получение всех задач
@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():

    try:
        full_info = db.get_all_info()
        return jsonify(full_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Удаление задачи по ID
@app.route('/api/tasks/id', methods=['DELETE'])
def delete_id_tasks():
    if not request.is_json:
        return jsonify({"error": "Должно быть в виде JSON"}), 400
    try:

        task_id = request.get_json()
        success = db.delete_only_id_tasks(list(task_id["id"]))
        match success:
            case True:
                return jsonify({"success": "Удалил все задачи, которые нашел"}), 201
            case False:
                return jsonify({"error": "Нет корректных id"}), 404
            case "Ошибка":
                return jsonify({"error": "Ошибка при удалении задач"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/name',methods = ['DELETE'])
def delete_name():
    try:
        name_info = request.get_json()
        if  "username" in name_info:
            success = db.delete_user_tasks(name_info["username"])
            match success:
                case True:
                    return jsonify({"success": f"Задачи {name_info["username"]} удалены!"}), 201
                case False:
                    return jsonify({"error": f"Пользователь {name_info["username"]} не найден"}), 404
                case "Ошибка":
                    return jsonify({"error": "Ошибка при удалении задач по имени"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500          

@app.route('/api/tasks/all',methods = ['DELETE'])
def delete_all():
    success = db.delete_all()
    match success:
        case True:
            return jsonify({"success": "Ваша база данных очищена!"}), 201
        case "Ошибка":
            return jsonify({"error": "Ошибка при удалении задач "}), 404

