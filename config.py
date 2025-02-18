import os

# Detect if running inside Docker
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

# Use `host.docker.internal` inside Docker, otherwise use localhost
WEKAN_HOST = "host.docker.internal" if RUNNING_IN_DOCKER else "127.0.0.1"
BASE_URL = f"http://{WEKAN_HOST}:3000"
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


"""
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
USERNAME = os.getenv("USERNAME", "adminn")
PASSWORD = os.getenv("PASSWORD", "adminn")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

CARDS_CREATION_BATCH = int(os.getenv("CARDS_CREATION_BATCH", 6))
USE_RMQ = os.getenv("USE_RMQ", "False").lower() == "true"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

DELETE_QUEUE = os.getenv("DELETE_QUEUE", "delete_tasks")
CREATE_QUEUE = os.getenv("CREATE_QUEUE", "create_tasks")

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
"""

