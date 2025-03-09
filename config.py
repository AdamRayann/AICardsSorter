import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")  # Use Docker service name

USERNAME = "adminn"
PASSWORD = "adminn"
GROQ_API_KEY = "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"
CARDS_CREATION_BATCH = 6
USE_RMQ = False
RABBITMQ_HOST = "localhost"
DELETE_QUEUE = "delete_tasks"
CREATE_QUEUE = "create_tasks"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


