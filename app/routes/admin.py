from flask import render_template, redirect, url_for, flash, request,jsonify, abort
from flask_login import login_required, current_user
from app import app, database, bcrypt
from app.models import Usuario
from app.forms import FormCriarUsuario, FormEditarUsuario
from app.decorators import admin_required
from werkzeug.utils import secure_filename

from app.services.ai_health import deepseek_healthcheck


import os


@app.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin_dashboard():
    total_usuarios = Usuario.query.count()

    return render_template('admin/admin_dashboard.html',
                           total_usuarios=total_usuarios,
                           ai_selftest_enabled=app.config.get('ENABLE_AI_SELFTEST', False))


@app.route("/create_user", methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_user():
    form = FormCriarUsuario()
    if form.validate_on_submit():
        nome_inicial = form.nome.data[:3].lower()
        cpf_inicial = form.cpf.data[:3]
        senha_gerada = f"{nome_inicial}{cpf_inicial}"
        senha_crypt = bcrypt.generate_password_hash(senha_gerada).decode('utf-8')

        usuario = Usuario(
            nome=form.nome.data,
            cpf=form.cpf.data,
            whatsapp=form.whatsapp.data,
            email=form.email.data.lower(),
            senha=senha_crypt
        )
        database.session.add(usuario)
        database.session.commit()
        flash(f'Usuário criado com e-mail: {form.email.data}. Senha inicial: {senha_gerada}', 'success')
        return redirect(url_for('listar_usuarios'))

    return render_template('admin/admin_create_user.html', form=form)


@app.route('/admin/usuarios', methods=['GET'])
@login_required
@admin_required
def listar_usuarios():
    nome = request.args.get('nome', type=str)
    email = request.args.get('email', type=str)
    cpf = request.args.get('cpf', type=str)
    whatsapp = request.args.get('whatsapp', type=str)

    query = Usuario.query
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
    if email:
        query = query.filter(Usuario.email.ilike(f"%{email}%"))
    if cpf:
        query = query.filter(Usuario.cpf.ilike(f"%{cpf}%"))
    if whatsapp:
        query = query.filter(Usuario.whatsapp.ilike(f"%{whatsapp}%"))

    usuarios = query.all()
    return render_template('admin/admin_listar_usuarios.html', usuarios=usuarios)


@app.route('/admin/usuario/<int:usuario_id>', methods=['GET'])
@login_required
@admin_required
def detalhar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('admin/admin_detalhar_usuario.html', usuario=usuario)


@app.route('/admin/usuario/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    form = FormEditarUsuario(obj=usuario)
    form.usuario_id.data = usuario.id

    if form.validate_on_submit():
        usuario.nome = form.nome.data
        usuario.email = form.email.data.lower()
        usuario.cpf = form.cpf.data
        usuario.whatsapp = form.whatsapp.data
        usuario.is_admin = form.is_admin.data == 1
        usuario.is_validated = form.is_validated.data

        try:
            database.session.commit()
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            database.session.rollback()
            flash('Erro ao salvar alterações. Tente novamente.', 'danger')

    return render_template('admin/admin_editar_usuario.html', form=form, usuario=usuario)


@app.route('/admin/usuario/<int:usuario_id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    database.session.delete(usuario)
    database.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('listar_usuarios'))


@app.route('/upload', methods=['POST'])
@login_required
@admin_required
def upload_file():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado', 'danger')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(request.url)

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.root_path, 'static/Midia/fotos', filename)
    file.save(file_path)

    flash('Arquivo salvo com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))


#########TESTE IA
@app.route("/_ai/selftest", methods=["GET"])
@login_required
@admin_required
def ai_selftest():
    if not app.config.get('ENABLE_AI_SELFTEST', False):
        return abort(404)  # oculta a existência da rota quando desativada
    result = deepseek_healthcheck()
    return jsonify(result), 200


