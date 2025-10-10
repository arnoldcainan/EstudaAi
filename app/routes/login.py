from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import app, database, bcrypt
from app.forms import FormLogin
from app.models import Usuario
import random, string
from captcha.image import ImageCaptcha

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form_login = FormLogin()
    next_page = request.args.get('next')

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        captcha_resposta = request.form.get("captcha").upper()

        if captcha_resposta != session.get("captcha_texto"):
            flash("CAPTCHA inválido. Tente novamente.", "danger")
            return redirect(url_for("login"))

        usuario = Usuario.query.filter_by(email=form_login.email.data.lower()).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)

            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('home')

            flash(f'Login realizado com sucesso! Bem-vindo, {usuario.nome}.', 'success')
            return redirect(next_page)
        else:
            flash('Email ou senha incorretos.', 'danger')

    return render_template('login.html', form_login=form_login, next=next_page)


@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('home'))


@app.route("/captcha")
def gerar_captcha():
    texto = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    session["captcha_texto"] = texto
    image_captcha = ImageCaptcha()
    data = image_captcha.generate(texto)
    return data.getvalue(), 200, {'Content-Type': 'image/png'}


@app.route("/validar_captcha", methods=["POST"])
def validar_captcha():
    resposta = request.form.get("captcha").upper()
    if resposta == session.get("captcha_texto"):
        flash("CAPTCHA validado com sucesso!", "success")
    else:
        flash("CAPTCHA inválido. Tente novamente.", "danger")
    return redirect(url_for('login'))
