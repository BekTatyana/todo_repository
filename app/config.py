from dotenv import load_dotenv
import os


load_dotenv()


class Config:
    
    database_url = os.getenv("url", "")
    telegram_token = os.getenv("token", "")
    key_admin = os.getenv("super_key","")


config=Config()