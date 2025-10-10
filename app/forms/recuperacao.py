from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class FormSolicitarRecuperacao(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Recuperação de Senha')

class FormRedefinirSenha(FlaskForm):
    nova_senha = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6, max=20)])
    confirmacao_senha = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired(), EqualTo('nova_senha', message='As senhas devem coincidir.')])
    submit = SubmitField('Redefinir Senha')
