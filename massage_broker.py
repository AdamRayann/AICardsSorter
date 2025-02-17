# Import RabbitMQ only if needed
import json

import config

if config.USE_RMQ:
    import pika


def send_to_rabbitmq(queue_name, message):
    """Send a message to RabbitMQ if enabled."""
    if not config.USE_RMQ:
        return

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    print(f"Sent message to {queue_name}: {message}")