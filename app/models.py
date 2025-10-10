from app import database, login_manager
from datetime import datetime, date
from flask_login import UserMixin
from pytz import timezone

from sqlalchemy import JSON, UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

def now_brazil():
    """Retorna a data e hora atual no fuso horário de Brasília."""
    fuso_brasilia = timezone('America/Sao_Paulo')
    return datetime.now(fuso_brasilia)


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    foto_perfil = database.Column(database.Text, nullable=True)
    nome = database.Column(database.String(100), nullable=False)
    cpf = database.Column(database.String(14), unique=True, nullable=False)
    whatsapp = database.Column(database.String(15), nullable=False)
    email = database.Column(database.String(100), unique=True, nullable=False)
    senha = database.Column(database.String(200), nullable=False)
    data_cadastro = database.Column(database.DateTime, default=now_brazil, nullable=False)
    is_admin = database.Column(database.Boolean, default=False)
    is_validated = database.Column(database.Boolean, default=False)



