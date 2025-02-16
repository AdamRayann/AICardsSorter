import json
import pika
import aiohttp
import asyncio
import config
import wekan_api


async def delete_card(card_id, board_id, list_id):
    """Deletes a card from Wekan asynchronously."""
    url = f"{config.BASE_URL}/api/boards/{board_id}/lists/{list_id}/cards/{card_id}"
    async with aiohttp.ClientSession() as session:
        print(wekan_api.HEADERS)
        async with session.delete(url, headers=wekan_api.HEADERS) as response:
            response_text = await response.text()
            if response.status == 200:
                print(f"Deleted card {card_id}")
            else:
                print(f"Failed to delete {card_id}: {response.status} | {response_text}")

def callback(ch, method, properties, body):
    """Handles messages from RabbitMQ queue."""
    data = json.loads(body)
    asyncio.run(delete_card(data["card_id"], data["board_id"], data["list_id"]))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    wekan_api.get_api_token()
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=config.DELETE_QUEUE, durable=True)
    channel.basic_consume(queue=config.DELETE_QUEUE, on_message_callback=callback)
    print("Delete Worker Listening...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
