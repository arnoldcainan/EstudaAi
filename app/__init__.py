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

# Caminho explícito para templates e static
base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))

# Demais configurações seguem normalmente...
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

# #####API ASAAS
# app.config['ASAAS_API_KEY'] = os.getenv('ASAAS_API_KEY')
# app.config['ASAAS_BASE_URL'] = os.getenv('ASAAS_BASE_URL')
# app.config['ASAAS_WEBHOOK_TOKEN'] = os.getenv('ASAAS_WEBHOOK_TOKEN')

# Diretório base para uploads dentro da pasta static
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Diretórios específicos para boletos e comprovantes
app.config['UPLOAD_BOLETOS'] = os.path.join(app.config['UPLOAD_FOLDER'], 'boletos')
app.config['UPLOAD_COMPROVANTES'] = os.path.join(app.config['UPLOAD_FOLDER'], 'comprovantes')

# Cria os diretórios se não existirem
os.makedirs(app.config['UPLOAD_BOLETOS'], exist_ok=True)
os.makedirs(app.config['UPLOAD_COMPROVANTES'], exist_ok=True)

# Inicializações
database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Configurações do Flask-Login
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Inicialização do banco de dados e importação de rotas
from app import models
engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sqlalchemy.inspect(engine)
if not inspector.has_table("usuario"):
    with app.app_context():
        database.drop_all()
        database.create_all()
        print("Base de dados criada")
else:
    print("Base de dados já existente")
from .filters import register_template_filters
register_template_filters(app)
from app.routes import *
