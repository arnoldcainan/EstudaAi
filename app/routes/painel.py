from flask import render_template
from flask_login import login_required, current_user

import os

from app import app
from app.models import Estudo

UPLOAD_FOLDER = os.getenv('UPLOAD_DIR', os.path.join(os.getcwd(), 'app', 'static', 'uploads'))
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    """Verifica a extensão do arquivo."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/painel', methods=['GET'])
@login_required
def painel_usuario():
    todos_estudos = Estudo.query.filter_by(user_id=current_user.id) \
        .order_by(Estudo.data_criacao.desc()).all()

    estudos_prontos = [e for e in todos_estudos if e.status == 'pronto']

    estudos_concluidos = [e for e in estudos_prontos if e.foi_respondido]

    total_respondidos = len(estudos_concluidos)

    soma_notas = sum([e.aproveitamento for e in estudos_concluidos])
    score_medio = int(soma_notas / total_respondidos) if total_respondidos > 0 else 0
    estudos_pendentes = [e for e in estudos_prontos if not e.foi_respondido]

    return render_template(
        'user/painel_usuario.html',
        usuario=current_user,
        ultimos_estudos=todos_estudos,  # Passamos a lista completa para iterar
        total_estudos_feitos=total_respondidos,
        score_medio=score_medio,
        qtd_pendentes=len(estudos_pendentes)
    )


