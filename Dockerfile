# Usa uma imagem Python leve
FROM python:3.11-slim

# Define a variável de ambiente para Python
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências (assumindo que requirements.txt está na raiz)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . /app

# Comando de inicialização do Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]