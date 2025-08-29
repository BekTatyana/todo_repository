from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from app.config import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'workers_names'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'home_tasks'
    task_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('workers_names.user_id'), nullable=False)
    task = Column(Text, nullable=False)
    
    user = relationship("User", back_populates="tasks")


class Database:
    def __init__(self):
        try:
            database_url = config.database_url
            self.engine = create_engine(database_url, echo=False)  
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
        except SQLAlchemyError:
            raise

    def save_tasks(self, username, tasks):
        try:
            username = username.lower().title()
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username)
                self.session.add(user)
                self.session.flush()
            
            for task in tasks:
                if task:
                    new_task = Task(task=task, user=user)
                    self.session.add(new_task)
                    self.session.commit()
            
            return "Задачи добавлены в БД"
            
        except Exception:
            self.session.rollback()
            return "Произошла ошибка при сохранении"
        finally: 
            self.session.close()
          
    def get_all_info(self):
        try:
            users = self.session.query(User).order_by(User.username).all()
            tasks = self.session.query(Task).order_by(Task.task).all()

            if not users or not tasks:
                return 'Нет пользователей или задач'
            
            full_info = {}

            for user in users:
                task_and_id = []
                if not user.tasks: 
                    continue 
                for task in user.tasks:
                    task_and_id.append(f"[{task.task_id}] {task.task}")
                if task_and_id:
                    full_info[user.username] = task_and_id

            return full_info
        
        except Exception:
            return "Ошибка при получении данных"
            
        finally: 
            self.session.close()

    def delete_user_tasks(self, username):
        try:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                return "Имя не найдено" 
            
            self.session.query(Task).filter(Task.user_id == user.user_id).delete()
            self.session.commit()

            return "Данные удалены успешно"
            
        except Exception:
            self.session.rollback()
            return False
        finally: 
            self.session.close()

    def delete_all(self):
        try:
            self.session.query(Task).delete()
            self.session.query(User).delete()
            self.session.commit()
            return "Все данные успешно удалены"
            
        except Exception:
            self.session.rollback()
            return False

        finally: 
            self.session.close()    

    def delete_only_id_tasks(self, ids):
        try:   
            if not ids:
                return "Вы не дали id для удаления"
            
            self.session.query(Task).filter(Task.task_id.in_(ids)).delete()
            self.session.commit()
            return "Операция успешна, удалил все данные, которые нашел"

        except Exception:
            self.session.rollback()
            return False
        
        finally: 
            self.session.close()