from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import app, database, bcrypt, mail, s
from app.forms import FormCriarConta, FormSolicitarRecuperacao, FormRedefinirSenha
from app.models import Usuario
from itsdangerous import SignatureExpired, BadSignature
from flask_mail import Message


import base64
from io import BytesIO
from PIL import Image


@app.route("/createlogin", methods=['GET', 'POST'])
def createlogin():
    if current_user.is_authenticated:
        flash('Você já está logado. Não é possível criar outra conta.', 'info')
        return redirect(url_for('home'))

    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha_crypt = bcrypt.generate_password_hash(form_criarconta.senha.data).decode("utf-8")
        usuario = Usuario(
            nome=form_criarconta.nome.data,
            cpf=form_criarconta.cpf.data,
            whatsapp=form_criarconta.whatsapp.data,
            email=form_criarconta.email.data.lower(),
            senha=senha_crypt,
            is_validated=True  # por segurança, já cria como não validado
        )
        database.session.add(usuario)
        database.session.commit()

        flash('Conta criada com sucesso!.', 'info')
        return redirect(url_for('login'))

    return render_template('createlogin.html', form=form_criarconta)



@app.route('/esqueci-senha', methods=["GET", "POST"])
def esqueci_senha():
    form = FormSolicitarRecuperacao()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data.lower()).first()
        if usuario:
            try:
                token = s.dumps(usuario.email, salt='recuperar-senha-salt')
                link = url_for('resetar_senha', token=token, _external=True)
                body_text = f"Olá, {usuario.nome}! Você solicitou a redefinição de senha. Clique no link para continuar: {link}"

                msg = Message(
                    subject="Recuperação de Senha",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[usuario.email],
                    body=body_text
                )
                mail.send(msg)
                flash('Um e-mail foi enviado com instruções para redefinir sua senha.', 'success')
            except Exception as e:
                flash('Não foi possível enviar o e-mail. Tente novamente mais tarde.', 'danger')
        else:
            flash('Se o e-mail estiver cadastrado, você receberá as instruções por e-mail.', 'info')

        return redirect(url_for('home'))

    return render_template('esqueci-senha.html', form=form)


@app.route('/resetar-senha/<token>', methods=["GET", "POST"])
def resetar_senha(token):
    try:
        email = s.loads(token, salt='recuperar-senha-salt', max_age=3600)
    except (SignatureExpired, BadSignature):
        flash('O link de recuperação é inválido ou expirou.', 'danger')
        return redirect(url_for('esqueci_senha'))

    form = FormRedefinirSenha()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            usuario.senha = bcrypt.generate_password_hash(form.nova_senha.data).decode('utf-8')
            database.session.commit()
            flash('Sua senha foi atualizada com sucesso!', 'success')
            return redirect(url_for('login'))

    return render_template('resetar-senha.html', form=form, token=token)





def converter_imagem_para_base64(file_storage):
    """
    Converte um arquivo de imagem (FileStorage) para string base64.
    Retorna None se o arquivo estiver vazio.
    """
    if not file_storage or file_storage.filename == '':
        return None

    try:
        imagem_bytes = file_storage.read()
        return base64.b64encode(imagem_bytes).decode('utf-8')
    except Exception as e:
        print(f"Erro ao converter imagem: {e}")
        return None



