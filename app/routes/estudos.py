from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

import os

from app import app, database
from app.models import Estudo
from app.services.task_producer import send_ai_task

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/novo-estudo', methods=['GET', 'POST'])
@login_required
def novo_estudo():
    # Renderiza o formulário de upload se for um GET
    if request.method == 'GET':
        return render_template(
            'user/novo_estudo.html',
            usuario=current_user,
            titulo_pagina='Novo Estudo'
        )

    # Lógica POST (Upload)
    if request.method == 'POST':
        # 1. Coleta e Validação
        file = request.files.get('documento')
        nome_estudo = request.form.get('nome_estudo')

        if not file or file.filename == '' or not allowed_file(file.filename):
            flash('Por favor, selecione um arquivo válido (PDF, DOCX, TXT).', 'danger')
            return redirect(request.url)

        # 2. Salvar Arquivo Localmente
        # Cria a pasta se não existir
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        filename = secure_filename(file.filename)
        # Caminho completo para SALVAR no Windows (necessário para o Python escrever o arquivo)
        file_path_windows = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(file_path_windows)
            app.logger.info(f"[Flask WEB] Arquivo salvo em: {file_path_windows}")
        except Exception as e:
            flash(f'Erro ao salvar arquivo temporário: {e}', 'danger')
            return redirect(request.url)

        # 3. CRIA REGISTRO INICIAL NO DB
        try:
            novo_estudo = Estudo(
                user_id=current_user.id,
                titulo=nome_estudo or filename,
                resumo="Aguardando processamento da IA...",
                status='processando',
                # DICA: Salve apenas o nome do arquivo no banco.
                # Isso evita que caminhos do Windows ("C:\Users...") quebrem visualização no Linux/Web.
                caminho_arquivo=filename
            )
            database.session.add(novo_estudo)
            database.session.commit()

            # --- 4. CHAMA O PRODUTOR RABBITMQ ---
            app.logger.info(f"[Flask WEB] Enviando tarefa. ID: {novo_estudo.id}, Arquivo: {filename}")

            # CORREÇÃO CRÍTICA AQUI:
            # Passamos 'filename' em vez de 'file_path'.
            # O Worker dentro do Docker saberá onde procurar na pasta dele (/app/static/uploads).
            send_ai_task(
                estudo_id=novo_estudo.id,
                filename=filename,
                user_id=current_user.id
            )

            flash('✅ Upload recebido! O processamento de IA foi iniciado. Acompanhe no Dashboard.', 'info')
            return redirect(url_for('painel_usuario'))

        except ConnectionError as e:
            # Rollback em caso de erro no RabbitMQ
            database.session.delete(novo_estudo)
            database.session.commit()
            if os.path.exists(file_path_windows):
                os.remove(file_path_windows)

            flash(f"❌ Erro de conexão com a fila: {e}", 'danger')
            return redirect(url_for('novo_estudo'))

        except Exception as e:
            # Rollback genérico
            database.session.rollback()
            if os.path.exists(file_path_windows):
                os.remove(file_path_windows)
            flash(f"❌ Erro ao iniciar a tarefa: {e}", 'danger')
            return redirect(url_for('novo_estudo'))

@app.route('/estudo/<int:estudo_id>')
@login_required
def visualizar_estudo(estudo_id):
    """
    Exibe um único estudo processado, com seu resumo e QCM.
    """
    # 1. Busca o estudo e garante que ele existe
    # (Usando database.session.get, que é o padrão moderno do SQLAlchemy)
    estudo = database.session.get(Estudo, estudo_id)
    if not estudo:
        abort(404)  # Estudo não encontrado

    # 2. (IMPORTANTE) Garante que o usuário logado é o dono do estudo
    if estudo.user_id != current_user.id:
        abort(403)  # Proibido (Forbidden), não é o dono

    # 3. (IMPORTANTE) Garante que o estudo está 'pronto'
    #    Se não estiver, redireciona de volta ao painel
    if estudo.status != 'pronto':
        flash('Este material ainda está sendo processado ou falhou.', 'info')
        return redirect(url_for('painel_usuario'))

    # 4. Busca as questões relacionadas
    #    (O .all() executa a query, já que a relação é 'lazy')
    questoes_list = estudo.questoes.all()

    # 5. Renderiza um *novo* template que criaremos no Passo 2
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

    # Itera sobre as questões do estudo
    acertos = 0
    total_questoes = 0

    questoes = estudo.questoes.all()

    for questao in questoes:
        # O nome do input no HTML será 'questao-ID_DA_QUESTAO'
        resposta_enviada = request.form.get(f'questao-{questao.id}')

        if resposta_enviada:
            questao.resposta_usuario = resposta_enviada

            # Compara a resposta enviada com a correta (strip para evitar erros de espaços)
            if resposta_enviada.strip() == questao.resposta_correta.strip():
                questao.correta = True
                acertos += 1
            else:
                questao.correta = False

        total_questoes += 1

    database.session.commit()

    flash(f'Correção concluída! Você acertou {acertos} de {total_questoes} questões.', 'success')
    return redirect(url_for('visualizar_estudo', estudo_id=estudo.id))