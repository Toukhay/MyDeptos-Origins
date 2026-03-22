import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    @staticmethod
    def validate():
        if not os.getenv('SECRET_KEY'):
            raise ValueError("SECRET_KEY no está definida en el archivo .env")
        if not os.getenv('DATABASE_URL'):
            raise ValueError("DATABASE_URL no está definida en el archivo .env")