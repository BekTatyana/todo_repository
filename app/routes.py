
from app import app, db
from pydantic import ValidationError
from app.utils.xlsx_and_csv import xlsx_csv
from app.utils.pydantic_file import AddTask, IdDel, NameDel
from fastapi import FastAPI,  HTTPException, Request
from fastapi.security import HTTPBasic


security = HTTPBasic()
app = FastAPI()

# Добавление задач
@app.post('/api/tasks', status_code=201)
def add_tasks():
    try:
        data = AddTask.model_validate(Request.json)
        username = data.username
        tasks = data.tasks
        
        result_save = db.save_tasks(username, tasks)
        info_from_data = db.get_all_info()
        xlsxcsv = xlsx_csv(info_from_data)
        result_csv = xlsxcsv.add_to_csv()
        result_xlsx = xlsxcsv.add_to_xlsx()
        
        result_for_all = {
            "Database": result_save,
            "Csv": result_csv,
            "Xlsx": result_xlsx
        }

        return result_for_all
        
    except ValidationError :
        raise HTTPException(status_code=400, detail=data)

# Получение всех задач
@app.get('/api/tasks')
def get_all_tasks():
    try:
        full_info = db.get_all_info()
        return full_info
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Удаление задачи по ID
@app.delete('/api/tasks/id', status_code=200)
def delete_id_tasks():
    try:
        data = IdDel.model_validate(Request.json)
        task_ids = data.id
        
        success = db.delete_only_id_tasks(task_ids)
        if not success:
            raise HTTPException(status_code=404, detail="При удалении задач произошла ошибка")

        return {"Успех": success}
         
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Удаление задач по имени пользователя
@app.delete('/api/tasks/name', status_code=200)
def delete_name():
    try:
        data = NameDel.model_validate(Request.json)
        username = data.username  
        
        if not username:
            raise HTTPException(status_code=400, detail="Необходимо имя пользователя")
        
        success = db.delete_user_tasks(username)
        if not success:
            raise HTTPException(status_code=404, detail="При удалении задач произошла ошибка")
            
        return {"success": success}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Удаление всех задач
@app.delete('/api/tasks/all', status_code=200)
def delete_all():
    try:
        success = db.delete_all()
        if not success:
            raise HTTPException(status_code=404, detail="При удалении задач произошла ошибка")
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

