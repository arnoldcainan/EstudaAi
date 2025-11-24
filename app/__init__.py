from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
import sqlalchemy
from dotenv import load_dotenv
import os

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///projeto.db')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
#INTEGRATION AI
app.config['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY')
app.config['DEEPSEEK_ENDPOINT'] = os.getenv('DEEPSEEK_ENDPOINT', 'https://api.deepseek.com/chat/completions')

app.config['ENABLE_AI_SELFTEST'] = os.getenv('ENABLE_AI_SELFTEST', 'False') == 'True'

###GOOGLE

app.config['GA_TRACKING_ID'] = 'G-QQ23BG6WBV'


app.config['API_KEY'] = os.getenv('API_KEY')


app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app import models


# engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
# inspector = sqlalchemy.inspect(engine)
# if not inspector.has_table("usuario"):
#     with app.app_context():
#         #database.drop_all()
#         database.create_all()
#         print("Base de dados criada")
# else:
#     print("Base de dados já existente")
# # Cria tabelas se ainda não existirem; sem "drop_all"


with app.app_context():
    inspector = sqlalchemy.inspect(database.engine)
    if "usuario" not in inspector.get_table_names():
        database.create_all()
        print("Base de dados criada")
    else:
        print("Base de dados já existente")

from .filters import register_template_filters
register_template_filters(app)
from app.routes import *
