from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.ai_processor import process_study_material
from app import database
from app.services.task_producer import send_ai_task
import os
from app import app
from app.filters import asdict as _as_dict  # ✅ importar função pura

# --- Imports da Aplicação (CRUCIAIS) ---
from app import app, database # Instância do Flask e SQLAlchemy
from app.models import Estudo, Questao # Modelos para persistência (Resolve 'Estudo')
from app.services.task_producer import send_ai_task # Produtor RabbitMQ (Seu novo serviço)
# ----------------------------------------

# Configuração de Uploads (Variáveis globais do módulo)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    """Verifica a extensão do arquivo."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/painel', methods=['GET'])
@login_required
def painel_usuario():
    # 1. Carregar dados REAIS do DB
    ultimos_estudos = Estudo.query.filter_by(user_id=current_user.id) \
        .order_by(Estudo.data_criacao.desc()) \
        .limit(5).all()

    # 2. Simular estatísticas gerais (Você pode substituí-las por consultas DB reais depois)
    # Total de estudos concluídos
    total_estudos_feitos = Estudo.query.filter_by(user_id=current_user.id, status='pronto').count()
    # Total de questões (simulado por enquanto, pois o QCM está nas relações)
    total_qcms = total_estudos_feitos * 5
    score_medio = 78  # Valor hardcoded, substitua por consulta de agregação no DB

    return render_template(
        'user/painel_usuario.html',
        usuario=current_user,
        # Variáveis atualizadas
        ultimos_estudos=ultimos_estudos,

        # Variáveis de estatísticas simuladas
        total_estudos_feitos=total_estudos_feitos,
        total_qcms=total_qcms,
        score_medio=score_medio
    )

# app/routes/painel.py (Função novo_estudo)

# NOVA ROTA DE NOVO ESTUDO
@app.route('/novo-estudo', methods=['GET', 'POST'])
@login_required
def novo_estudo():
    # Renderiza o formulário de upload se for um GET
    if request.method == 'GET':
        # Renderiza com o caminho ajustado 'user/novo_estudo.html' se for o caso
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

        # 2. Salvar Arquivo Localmente (Define filename e file_path)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)  # Define 'filename'
        file_path = os.path.join(UPLOAD_FOLDER, filename)  # Define 'file_path'

        try:
            file.save(file_path)
            # --- DEBUG PRINT ---
            app.logger.info(f"[Flask WEB] Arquivo salvo em (caminho absoluto): {file_path}")
            # ---------------------
        except Exception as e:
            flash(f'Erro ao salvar arquivo temporário: {e}', 'danger')
            return redirect(request.url)

        # 3. CRIA REGISTRO INICIAL NO DB (STATUS "PROCESSANDO")
        try:
            novo_estudo = Estudo(  # Resolve 'Estudo'
                user_id=current_user.id,
                titulo=nome_estudo or filename,
                resumo="Processamento de IA iniciado...",
                status='processando',
                caminho_arquivo=file_path
            )
            database.session.add(novo_estudo)
            database.session.commit()

            # --- 4. CHAMA O PRODUTOR RABBITMQ (ASSÍNCRONO) ---
            # --- DEBUG PRINT ---
            app.logger.info(
                f"[Flask WEB] Enviando tarefa para RabbitMQ: (Estudo ID: {novo_estudo.id}, Path: {file_path})")
            # ---------------------
            send_ai_task(  # Resolve 'send_ai_task'
                estudo_id=novo_estudo.id,
                file_path=file_path,  # Resolve 'file_path'
                user_id=current_user.id
            )

            flash(
                '✅ Upload recebido! O processamento de IA foi iniciado em segundo plano. Acompanhe o status no Dashboard.',
                'info')
            return redirect(url_for('painel_usuario'))

        except ConnectionError as e:
            # Em caso de falha no RabbitMQ, limpamos o DB e o arquivo
            database.session.delete(novo_estudo)
            database.session.commit()
            if os.path.exists(file_path):
                os.remove(file_path)

            flash(f"❌ Erro de serviço: {e}. Tente novamente mais tarde.", 'danger')
            # CORREÇÃO: url_for deve ser usado com nome de rota, não caminho de template
            return redirect(url_for('novo_estudo'))

        except Exception as e:
            # Tratamento de erro genérico do DB/commit
            database.session.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f"❌ Erro ao iniciar a tarefa: {e}. Tente novamente.", 'danger')
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