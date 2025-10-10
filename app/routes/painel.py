from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user


from app import app
from app.filters import asdict as _as_dict  # ✅ importar função pura


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
        'painel_usuario.html',
        usuario=current_user,
        ultimos_resumos_simulados=ultimos_resumos_simulados
    )


# NOVA ROTA DE NOVO ESTUDO
@app.route('/novo-estudo', methods=['GET', 'POST'])
@login_required
def novo_estudo():
    if request.method == 'POST':
        # --- A lógica de upload e chamada da IA será adicionada aqui ---
        # 1. Checar se o arquivo foi enviado
        if 'documento' not in request.files:
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)

        file = request.files['documento']

        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)

        # 2. Se o arquivo estiver OK, chamaremos o serviço de IA aqui (em breve)

        flash('Upload recebido. Processamento em andamento...', 'info')
        # Por enquanto, redireciona para o painel
        return redirect(url_for('painel_usuario'))

    # Se for GET, renderiza o formulário de upload
    return render_template(
        'novo_estudo.html',
        usuario=current_user,
        # Adicione o título da página
        titulo_pagina='Novo Estudo'
    )