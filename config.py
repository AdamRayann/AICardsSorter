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


