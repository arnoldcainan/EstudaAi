from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import NoCredentialsError

import os

from app import app, database
from app.models import Estudo
from app.services.task_producer import send_ai_task

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY')
    )

@app.route('/novo-estudo', methods=['GET', 'POST'])
@login_required
def novo_estudo():
    if request.method == 'GET':
        return render_template(
            'user/novo_estudo.html',
            usuario=current_user,
            titulo_pagina='Novo Estudo'
        )

    if request.method == 'POST':
        # 1. Coleta e Validação
        file = request.files.get('documento')
        nome_estudo = request.form.get('nome_estudo')

        if not file or file.filename == '' or not allowed_file(file.filename):
            flash('Por favor, selecione um arquivo válido (PDF, DOCX, TXT).', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)

        try:
            r2 = get_r2_client()
            r2.upload_fileobj(
                file,
                os.getenv('R2_BUCKET_NAME'),
                filename
            )
            app.logger.info(f"[R2 Upload] Arquivo {filename} enviado para a nuvem.")
        except Exception as e:
            app.logger.error(f"Erro no R2: {e}")
            flash(f'Erro ao enviar arquivo para a nuvem: {e}', 'danger')
            return redirect(request.url)

        try:
            novo_estudo = Estudo(
                user_id=current_user.id,
                titulo=nome_estudo or filename,
                resumo="Aguardando processamento da IA...",
                status='processando',
                caminho_arquivo=filename
            )
            database.session.add(novo_estudo)
            database.session.commit()
            app.logger.info(f"[Flask WEB] Enviando tarefa. ID: {novo_estudo.id}, Arquivo: {filename}")

            send_ai_task(
                estudo_id=novo_estudo.id,
                filename=filename,
                user_id=current_user.id
            )

            flash('✅ Upload recebido! O processamento de IA foi iniciado.', 'info')
            return redirect(url_for('painel_usuario'))

        except Exception as e:
            database.session.rollback()
            app.logger.error(f"Erro ao registrar tarefa: {e}")
            flash(f"❌ Erro ao iniciar a tarefa: {e}", 'danger')
            return redirect(url_for('novo_estudo'))

@app.route('/estudo/<int:estudo_id>')
@login_required
def visualizar_estudo(estudo_id):
    """
    Exibe um único estudo processado, com seu resumo e QCM.
    """
    estudo = database.session.get(Estudo, estudo_id)
    if not estudo:
        abort(404)

    if estudo.user_id != current_user.id:
        abort(403)

    if estudo.status != 'pronto':
        flash('Este material ainda está sendo processado ou falhou.', 'info')
        return redirect(url_for('painel_usuario'))

    questoes_list = estudo.questoes.all()

    return render_template(
        'user/visualizar_estudo.html',
        usuario=current_user,
        estudo=estudo,
        questoes=questoes_list,
        titulo_pagina=estudo.titulo
    )


@app.route('/estudo/<int:estudo_id>/corrigir', methods=['POST'])
@login_required
def corrigir_estudo(estudo_id):
    estudo = database.session.get(Estudo, estudo_id)

    if not estudo or estudo.user_id != current_user.id:
        abort(403)

    acertos = 0
    total_questoes = 0

    questoes = estudo.questoes.all()

    for questao in questoes:
        resposta_enviada = request.form.get(f'questao-{questao.id}')

        if resposta_enviada:
            questao.resposta_usuario = resposta_enviada

            if resposta_enviada.strip() == questao.resposta_correta.strip():
                questao.correta = True
                acertos += 1
            else:
                questao.correta = False

        total_questoes += 1

    database.session.commit()

    flash(f'Correção concluída! Você acertou {acertos} de {total_questoes} questões.', 'success')
    return redirect(url_for('visualizar_estudo', estudo_id=estudo.id))