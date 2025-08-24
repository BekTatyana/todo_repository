from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey,Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import config

Base = declarative_base()


class UserAuth(Base):
    __tablename__ = 'login_password'
    login_id = Column(Integer, primary_key=True)  
    login = Column(String(45), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)

    tasks = relationship("Task", back_populates="auth", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def make_admin(self):
        self.is_admin = True


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
    login_id = Column( Integer,ForeignKey('login_password.login_id'),nullable=False)
    
    user = relationship("User", back_populates="tasks")
    auth = relationship("UserAuth", back_populates="tasks")


class Database:
    def __init__(self):
        try:
            database_url = config.database_url
            self.engine = create_engine(database_url, echo=False)  
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
        except SQLAlchemyError :
            raise

    def auth_user(self, login, password, super_key=None):

        try:
            info_login = self.session.query(UserAuth).filter_by(login=login).first()

            if info_login:
            
                if not info_login.check_password(password):
                    return False
            else:
           
                info_login = UserAuth(login=login)
                info_login.set_password(password)
                self.session.add(info_login)
                self.session.commit()  
        
        
            if super_key:
                if super_key != config.key_admin:
                    return "Неверный супер-пароль, доступ запрещен"
                info_login.make_admin()
                self.session.commit()
                return "Вход успешный, у вас есть права администратора"
        
            return True
    
        except Exception as e:
            self.session.rollback()
            print(f"Ошибка аутентификации: {e}")
            return "Ошибка при аутентификации"
        
        finally:
            self.session.close()

    def save_tasks(self, username, tasks, login):
        try:
            user_auth = self.session.query(UserAuth).filter_by(login=login).first()
            login_id = user_auth.login_id
            
            username = username.lower().title()
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username)
                self.session.add(user)
                self.session.flush()
            
            for task in tasks:
                if task:
                    new_task = Task(task=task, user=user, login_id=login_id)
                    self.session.add(new_task)
                    self.session.commit()
            
            return "Задачи добавлены в БД"
            
        except Exception :
            self.session.rollback()
            return "Произошла ошибка при сохранении"
        finally: 
            self.session.close()
          
    def get_all_info(self,login):
        try:
            user_auth = self.session.query(UserAuth).filter_by(login=login).first()
            login_id = user_auth.login_id

            full_info = {}

            if user_auth.is_admin:
                users = self.session.query(User).order_by(User.username).all()
                tasks = self.session.query(Task).order_by(Task.task).all()

            else:
                users = self.session.query(User).order_by(User.username).all()
                tasks = self.session.query(Task).filter(Task.login_id == login_id).order_by(Task.task).all()

            if not users or not tasks:
                return 'Нет пользователей или задач'
            
            full_info = {}

            for user in users:
                task_and_id = []
                if not user.tasks: 
                    continue 
                for task in user.tasks:
                    if user_auth.is_admin or task.login_id == login_id:
                        task_and_id.append( f"[{task.task_id}] {task.task}")
                if task_and_id:
                    full_info[user.username]= task_and_id

            return full_info
        
        except Exception :
            return "Ошибка при получении данных"
            
        finally: 
            self.session.close()

    def delete_user_tasks(self, username,login):
        try:
            info_login = self.session.query(UserAuth).filter_by(login=login).first()
            
            
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                return "Имя не найдено" 
            
            
            self.session.query(Task).filter(
                Task.user_id == user.user_id, 
                Task.login_id == info_login.login_id).delete()
            self.session.commit()

            return "Данные удалены успешно"
            
        except Exception:
            self.session.rollback()
            return False
        finally: 
            self.session.close()

    def delete_all(self,login):

        info_login = self.session.query(UserAuth).filter_by(login=login).first()

        if not info_login.is_admin:
            return "Доступ к удалению данных запрещен, у вас нет прав администратора"
        
        try:
            self.session.query(Task).delete()
            self.session.query(User).delete()
            self.session.commit()
            return "Все данные успешно удалены"
            
        except Exception :
            self.session.rollback()
            return False

        finally: 
            self.session.close()    

    def delete_only_id_tasks(self, ids, login):
        try:   
            info_login = self.session.query(UserAuth).filter_by(login=login).first()

            if not ids:
                return "Вы не дали id для удаления"
            
            if info_login.is_admin:
                self.session.query(Task).filter(Task.task_id.in_(ids)).delete()

            else:
                
                self.session.query(Task).filter(
                    Task.task_id.in_(ids),
                    Task.login_id == info_login.login_id  
                ).delete()

            self.session.commit()
            return "Операция успешна, удалил все данные, которые нашел"

        except Exception :
            self.session.rollback()
            return False
        
        finally: 

            self.session.close()