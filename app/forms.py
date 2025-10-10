from wtforms.validators import Length
from app.models import Usuario
import re
from wtforms import ValidationError, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, SelectField, HiddenField, DecimalField, IntegerField,DateField
from flask_wtf.file import FileField, FileAllowed

from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, InputRequired, Optional
from flask_wtf import FlaskForm
from flask_login import current_user
def validar_cpf(cpf_str):
    """
    Função que recebe apenas dígitos e valida o CPF.
    """
    cpf = [int(char) for char in cpf_str if char.isdigit()]  # já deve vir limpo, mas garantimos
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    # Cálculo do primeiro dígito verificador
    soma = sum(x * y for x, y in zip(cpf[:9], range(10, 1, -1)))
    d1 = (soma * 10 % 11) % 10
    if cpf[9] != d1:
        return False

    # Cálculo do segundo dígito verificador
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
    confirmacao_senha = PasswordField(
        'Confirme a Senha',
        validators=[DataRequired(), EqualTo('senha', message='As senhas devem coincidir.')]
    )
    aceite_termos = BooleanField('Aceito os termos de uso', validators=[DataRequired()])
    botao_submit = SubmitField('Criar conta')

    def validate_cpf(self, field):
        # Remove tudo que não for dígito: pontos, traços, espaços etc.
        cpf_limpo = re.sub(r'\D', '', field.data)

        # Atribui de volta ao field.data (assim, depois no banco, estará limpo)
        field.data = cpf_limpo

        # Agora usa a função de validação que só espera dígitos
        if not validar_cpf(cpf_limpo):
            raise ValidationError('CPF inválido.')

        # Verifica se já existe no banco de dados
        usuario = Usuario.query.filter_by(cpf=cpf_limpo).first()
        if usuario:
            raise ValidationError('Este CPF já está cadastrado.')

    def validate_email(self, field):
        usuario = Usuario.query.filter_by(email=field.data).first()
        if usuario:
            raise ValidationError('Este e-mail já está cadastrado')





class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    captcha = StringField("Captcha", validators=[DataRequired()])
    botao_submit_login = SubmitField('Fazer Login')


#ROTA DE RECOVERY

class FormSolicitarRecuperacao(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Recuperação de Senha')

class FormRedefinirSenha(FlaskForm):
    nova_senha = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6, max=20)])
    confirmacao_senha = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('nova_senha')])
    submit = SubmitField('Redefinir Senha')


class FormEditarUsuario(FlaskForm):
    usuario_id = HiddenField('ID do Usuário')  # Campo oculto para o ID
    nome = StringField('Nome', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(max=14)])  # Máscaras podem ser usadas no front-end
    whatsapp = StringField('WhatsApp', validators=[DataRequired(), Length(max=15)])
    is_admin = SelectField('É Administrador?', choices=[('1', 'Sim'), ('0', 'Não')], coerce=int)
    submit = SubmitField('Salvar')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        # Verifica se o email já existe, mas ignora o email do próprio usuário em edição
        if usuario and usuario.id != int(self.usuario_id.data):
            raise ValidationError('Este email já está cadastrado por outro usuário.')

    def validate_cpf(self, cpf):
        usuario = Usuario.query.filter_by(cpf=cpf.data).first()
        # Verifica se o CPF já existe, mas ignora o CPF do próprio usuário em edição
        if usuario and usuario.id != int(self.usuario_id.data):
            raise ValidationError('Este CPF já está cadastrado por outro usuário.')



############### OS
def usuario_choices():
    usuarios = Usuario.query.all()

    return usuarios


############  ADM CRIA USER

class FormCriarUsuario(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=3, message="O nome deve ter pelo menos 3 caracteres.")])
    cpf = StringField('CPF', validators=[DataRequired()])
    whatsapp = StringField('Whatsapp', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    botao_submit = SubmitField('Criar conta')

    def validate_cpf(self, field):
        # Remove tudo que não for dígito: pontos, traços, espaços etc.
        cpf_limpo = re.sub(r'\D', '', field.data)

        # Atribui de volta ao field.data (assim, depois no banco, estará limpo)
        field.data = cpf_limpo

        # Agora usa a função de validação que só espera dígitos
        if not validar_cpf(cpf_limpo):
            raise ValidationError('CPF inválido.')

        # Verifica se já existe no banco de dados
        usuario = Usuario.query.filter_by(cpf=cpf_limpo).first()
        if usuario:
            raise ValidationError('Este CPF já está cadastrado.')

    def validate_email(self, field):
        usuario = Usuario.query.filter_by(email=field.data).first()
        if usuario:
            raise ValidationError('Este e-mail já está cadastrado')





