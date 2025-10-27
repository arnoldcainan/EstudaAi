from app import database, login_manager
from datetime import datetime, date
from flask_login import UserMixin
from pytz import timezone


from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import json

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



############ ESTUDOS

class Estudo(database.Model):
    __tablename__ = 'estudos'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

    titulo = database.Column(database.String(255), nullable=False)
    data_criacao = database.Column(database.DateTime, default=now_brazil)

    # Conteúdo principal
    resumo = database.Column(database.Text, nullable=False)
    status = database.Column(database.String(50), default='pronto', nullable=False)
    caminho_arquivo = database.Column(database.String(512), nullable=True)

    # Relações
    questoes = database.relationship("Questao", backref="estudo", lazy='dynamic', cascade="all, delete-orphan")
    usuario = database.relationship("Usuario")


class Questao(database.Model):
    __tablename__ = 'questoes'

    id = database.Column(database.Integer, primary_key=True)
    estudo_id = database.Column(database.Integer, database.ForeignKey('estudos.id'), nullable=False)

    pergunta = database.Column(database.Text, nullable=False)

    # Armazena as opções como TEXT (string JSON)
    opcoes_json = database.Column(database.Text, nullable=False)
    resposta_correta = database.Column(database.String(255), nullable=False)

    # Campos de resultado do usuário
    resposta_usuario = database.Column(database.String(255), nullable=True)
    correta = database.Column(database.Boolean, nullable=True)