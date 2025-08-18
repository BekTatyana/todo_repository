html_text = """
<!DOCTYPE html>
<html>
<head>
    <title>API Документация</title>
</head>
<body>
    <h1>Документация API менеджера задач</h1>
    
    <h2>Добавить задачи</h2>
    <p><b>POST /api/tasks</b></p>
    <pre>{
  "username": "Имя",
  "tasks": "Задача1, Задача2"
}</pre>

    <h2>Посмотреть данные в бд</h2>
    <p><b>GET /api/tasks</b></p>
    <pre>Без параметров</pre>

    <h2>Удалить задачи по ID</h2>
    <p><b>DELETE /api/tasks/id</b></p>
    <pre>{
  "id": [1, 2, 3]
}</pre>

    <h2>Удалить все задачи пользователя</h2>
    <p><b>DELETE /api/tasks/name</b></p>
    <pre>{
  "username": "Имя"
}</pre>

    <h2>Удалить все задачи</h2>
    <p><b>DELETE /api/tasks/all</b></p>
    <p>Без параметров</p>

</body>
</html>"""