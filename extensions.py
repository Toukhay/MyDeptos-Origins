from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

mysql = MySQL()
login_manager = LoginManager()
csrf = CSRFProtect()