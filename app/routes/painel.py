from flask import render_template, redirect, url_for, flash, request
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



# Rota existente
@app.route('/painel', methods=['GET'])
@login_required
def painel_usuario():
    # ... (código existente) ...

    # 2. Carregar dados específicos do Estudo AI aqui (Ex: ultimos resumos, estatisticas)
    ultimos_resumos_simulados = [
        # Dados simulados para o painel
        {'id': 1, 'titulo': 'Introdução a Microserviços', 'data': '10/01/2024', 'paginas': 15, 'qcm_feito': True,
         'score': 85},
        {'id': 2, 'titulo': 'Padrões de Design com Python', 'data': '05/12/2023', 'paginas': 25, 'qcm_feito': False,
         'score': None},
    ]

    return render_template(
        'user/painel_usuario.html',
        usuario=current_user,
        ultimos_resumos_simulados=ultimos_resumos_simulados
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