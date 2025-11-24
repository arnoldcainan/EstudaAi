import pika
import json
import logging
import os

log = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'user_fallback')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'password_fallback')
VHOST = os.getenv('RABBITMQ_VHOST', '/')
QUEUE_NAME = 'ai_task_queue'


def send_ai_task(estudo_id: int, filename: str, user_id: int):
    connection = None
    try:
        log.info(f"Tentando conectar ao RabbitMQ em: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                virtual_host='/'
            )
        )

        if connection is None:
            raise ConnectionError("O objeto de conexão retornou vazio (None).")

        channel = connection.channel()

        # Declara a fila
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        payload = {
            'estudo_id': estudo_id,
            'filename': filename,
            'user_id': user_id,
        }

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)
        )
        log.info(f"Tarefa enviada com sucesso! Arquivo: {filename}")

    except pika.exceptions.AMQPConnectionError as e:
        log.error(f"ERRO DE CONEXÃO RABBITMQ: Não foi possível conectar em {RABBITMQ_HOST}:{RABBITMQ_PORT}. Erro: {e}")
        # Relança o erro para o Flask mostrar o Flash message
        raise ConnectionError(f"Falha ao conectar no RabbitMQ ({RABBITMQ_HOST})")

    except Exception as e:
        log.error(f"Erro inesperado no produtor: {e}")
        raise e

    finally:
        if connection and not connection.is_closed:
            connection.close()
