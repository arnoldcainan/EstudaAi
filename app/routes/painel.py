from flask import render_template
from flask_login import login_required, current_user

from app import app
from app.filters import asdict as _as_dict  # ✅ importar função pura


@app.route('/painel', methods=['GET'])
@login_required
def painel_usuario():
    # 1. Carregar o usuário logado (current_user)

    # 2. Carregar dados específicos do Estudo AI aqui (Ex: ultimos resumos, estatisticas)
    ultimos_resumos_simulados = [
        # ... (seus dados simulados ou do DB) ...
    ]

    return render_template(
        'painel_usuario.html',
        # Passando a variável 'usuario' para o template:
        usuario=current_user,
        ultimos_resumos_simulados=ultimos_resumos_simulados
        # ... (outras variáveis necessárias) ...
    )