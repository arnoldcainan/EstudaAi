from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, SelectField, DateField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import Usuario
import re

def validar_cpf(cpf_str):
    cpf = [int(char) for char in cpf_str if char.isdigit()]
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    soma = sum(x * y for x, y in zip(cpf[:9], range(10, 1, -1)))
    d1 = (soma * 10 % 11) % 10
    if cpf[9] != d1:
        return False
    soma = sum(x * y for x, y in zip(cpf[:10], range(11, 1, -1)))
    d2 = (soma * 10 % 11) % 10
    if cpf[10] != d2:
        return False
    return True

class FormCriarConta(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[DataRequired()])
    whatsapp = StringField('Whatsapp', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmacao_senha = PasswordField('Confirme a Senha', validators=[
        DataRequired(), EqualTo('senha', message='As senhas devem coincidir.')])
    aceite_termos = BooleanField('Aceito os termos de uso', validators=[DataRequired()])
    botao_submit = SubmitField('Criar conta')

    def validate_cpf(self, field):
        cpf_limpo = re.sub(r'\D', '', field.data)
        field.data = cpf_limpo
        if not validar_cpf(cpf_limpo):
            raise ValidationError('CPF inválido.')
        usuario = Usuario.query.filter_by(cpf=cpf_limpo).first()
        if usuario:
            raise ValidationError('Este CPF já está cadastrado.')

    def validate_email(self, field):
        usuario = Usuario.query.filter_by(email=field.data.lower()).first()
        if usuario:
            raise ValidationError('Este e-mail já está cadastrado.')

class FormCriarUsuario(FlaskForm):
    nome = StringField('Nome', validators=[
        DataRequired(), Length(min=3, message="O nome deve ter pelo menos 3 caracteres.")])
    cpf = StringField('CPF', validators=[DataRequired()])
    whatsapp = StringField('Whatsapp', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    botao_submit = SubmitField('Criar conta')

    def validate_cpf(self, field):
        cpf_limpo = re.sub(r'\D', '', field.data)
        field.data = cpf_limpo
        if not validar_cpf(cpf_limpo):
            raise ValidationError('CPF inválido.')
        usuario = Usuario.query.filter_by(cpf=cpf_limpo).first()
        if usuario:
            raise ValidationError('Este CPF já está cadastrado.')

    def validate_email(self, field):
        usuario = Usuario.query.filter_by(email=field.data.lower()).first()
        if usuario:
            raise ValidationError('Este e-mail já está cadastrado.')

class FormEditarUsuario(FlaskForm):
    usuario_id = HiddenField('ID do Usuário')
    nome = StringField('Nome', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(max=14)])
    whatsapp = StringField('WhatsApp', validators=[DataRequired(), Length(max=15)])
    is_admin = SelectField('É Administrador?', choices=[('1', 'Sim'), ('0', 'Não')], coerce=int)

    is_validated = BooleanField('Conta Validada')  # <-- novo campo aqui

    submit = SubmitField('Salvar')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data.lower()).first()
        if usuario and usuario.id != int(self.usuario_id.data):
            raise ValidationError('Este email já está cadastrado por outro usuário.')

    def validate_cpf(self, cpf):
        usuario = Usuario.query.filter_by(cpf=cpf.data).first()
        if usuario and usuario.id != int(self.usuario_id.data):
            raise ValidationError('Este CPF já está cadastrado por outro usuário.')

