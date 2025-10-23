from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from services. import process_study_material

from app import app
from app.filters import asdict as _as_dict  # ✅ importar função pura

# Pasta onde os arquivos serão salvos TEMPORARIAMENTE
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


# NOVA ROTA DE NOVO ESTUDO
@app.route('/novo-estudo', methods=['GET', 'POST'])
@login_required
def novo_estudo():
    if request.method == 'POST':
        file = request.files.get('documento')
        nome_estudo = request.form.get('nome_estudo')

        # 1. VALIDAÇÃO
        if not file or file.filename == '' or not allowed_file(file.filename):
            flash('Por favor, selecione um arquivo válido (PDF, DOCX, TXT).', 'danger')
            return redirect(request.url)

        # 2. SALVAR ARQUIVO LOCALMENTE (Temporário)
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # --- FASE 1: CHAMA O PROCESSAMENTO DE IA (SÍNCRONO) ---
        flash('Upload recebido. Processamento de IA iniciado, AGUARDE...', 'warning')

        # Este é o ponto BLOQUEANTE (o site vai esperar)
        ia_result = process_study_material(file_path, titulo=nome_estudo or filename)

        # 3. TRATAMENTO DE RESULTADO E PERSISTÊNCIA (Bloco 2.4)
        if ia_result['status'] == 'completed':
            # Aqui você salvaria no seu banco de dados (Modelo Estudo)
            # Ex: Estudo.create(user_id=current_user.id, **ia_result)

            # Limpa o arquivo após o uso (importante!)
            os.remove(file_path)

            flash('✅ Estudo gerado com sucesso! Você pode ver o resumo.', 'success')
            # Redireciona para a página de visualização do estudo (em breve)
            return redirect(url_for('painel_usuario'))

        else:
            # Limpa o arquivo mesmo em caso de falha
            os.remove(file_path)

            flash(f"❌ Falha ao processar o arquivo: {ia_result.get('error', 'Erro desconhecido.')}", 'danger')
            return redirect(url_for('novo_estudo'))

    # ... (código GET) ...
    return render_template(
        'novo_estudo.html',
        usuario=current_user,
        titulo_pagina='Novo Estudo'
    )