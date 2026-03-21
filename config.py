import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'bdmydeptos')
    SECRET_KEY = os.getenv('SECRET_KEY')

    @staticmethod
    def validate():
        if not os.getenv('SECRET_KEY'):
            raise ValueError("SECRET_KEY no está definida en el archivo .env")