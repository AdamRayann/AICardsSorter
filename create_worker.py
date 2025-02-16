import json
import pika
import requests
import config
import wekan_api


def create_card(data):
    """Creates a card in Wekan."""
    url = f"{config.BASE_URL}/api/boards/{data['board_id']}/lists/{data['list_id']}/cards"
    payload = {
        "title": data["title"],
        "description": "",
        "authorId": data["user_id"],
        "swimlaneId": data["swimlane_id"]
    }
    response = requests.post(url, json=payload, headers=wekan_api.HEADERS)
    print(f"Created card {data['title']}" if response.status_code == 200 else f"Failed to create {data['title']}")


# def cards_batch(data,CARDS_CREATION_BATCH=config.CARDS_CREATION_BATCH):
#     for i in range(0, len(sorted_titles), CARDS_CREATION_BATCH):
#         batch = sorted_titles[i:i + CARDS_CREATION_BATCH]
#         create_card_batch(batch, BOARD_ID, LIST_ID, SWIMLANE_ID, USER_ID)
#

def callback(ch, method, properties, body):
    """Handles messages from RabbitMQ queue."""
    data = json.loads(body)
    create_card(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    wekan_api.get_api_token()
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=config.CREATE_QUEUE, durable=True)
    channel.basic_consume(queue=config.CREATE_QUEUE, on_message_callback=callback)
    print("Create Worker Listening...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
