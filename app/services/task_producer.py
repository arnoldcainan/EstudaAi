# app/services/task_producer.py
import pika
import json
import logging
import os

log = logging.getLogger(__name__)

# Configurações do RabbitMQ: Lendo do .env ou variáveis de ambiente do Docker
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'user_fallback') # Use um fallback seguro
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'password_fallback')
VHOST = os.getenv('RABBITMQ_VHOST', '/') # VHost padrão
QUEUE_NAME = 'ai_task_queue'


def send_ai_task(estudo_id: int, file_path: str, user_id: int):
    """
    Publica uma mensagem na fila do RabbitMQ com os detalhes da tarefa de IA.
    :param estudo_id: ID do estudo recém-criado no DB.
    :param file_path: Caminho temporário do arquivo.
    :param user_id: ID do usuário para segurança.
    """
    connection = None
    try:
        # 1. Conexão
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                virtual_host = VHOST  # Adicione o VHOST
            )
        )
        channel = connection.channel()

        # 2. Declaração da Fila (Garante que a fila existe)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        # 3. Preparação da Mensagem (Payload)
        payload = {
            'estudo_id': estudo_id,
            'file_path': file_path,
            'user_id': user_id,
        }
        message_body = json.dumps(payload)

        # 4. Publicação da Mensagem
        channel.basic_publish(
            exchange='',  # Usando o exchange padrão
            routing_key=QUEUE_NAME,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent  # Mensagem persistente
            )
        )
        log.info(f"Tarefa de IA enviada para a fila {QUEUE_NAME} para Estudo ID: {estudo_id}")

    except pika.exceptions.AMQPConnectionError as e:
        log.error(f"Falha ao conectar ao RabbitMQ. A tarefa {estudo_id} NÃO foi enviada. Erro: {e}")
        # Em caso de falha, você pode querer logar a tarefa para tentar novamente depois
        raise ConnectionError("Falha na conexão com o serviço de fila (RabbitMQ).")

    finally:
        if connection:
            connection.close()

# --- FIM DO PRODUTOR ---