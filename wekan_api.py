import requests
import json
from config import BASE_URL, USERNAME, PASSWORD

HEADERS = {}


def get_api_token(username, password):
    """
    Logs into Wekan and retrieves an API token & user ID.
    """
    url = f"{BASE_URL}/users/login"
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    #print(f"Login API Response Status Code: {response.status_code}")
    #print(f"Login API Response Text: {response.text}")

    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        user_id = data.get("id")

        if not token:
            print("Error: Token not found in response!")
            return None

        #print(" API Token Retrieved:", token)
        #print("User ID:", user_id)

        global HEADERS
        HEADERS = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        return user_id, token
    else:
        print("Error: Unable to retrieve API token.")
        return None


def get_boards(user_id):
    """
    Fetch all boards for the user and find Board-AI.
    """
    url = f"{BASE_URL}/api/users/{user_id}/boards"
    response = requests.get(url, headers=HEADERS)

    #print("Status Code:", response.status_code)
    #print("Raw Response:", response.text)

    if response.status_code == 200:
        try:
            boards = response.json()
            for board in boards:
                if board["title"] == "Board-AI":
                    return board["_id"]
            print("Board-AI not found!")
            return None
        except requests.exceptions.JSONDecodeError:
            print("Error: Response is not valid JSON.")
            return None
    else:
        print("Error fetching boards:", response.text)
        return None


def get_lists(board_id):
    """
    Fetch all lists in Board-AI and find List-AI.
    """
    url = f"{BASE_URL}/api/boards/{board_id}/lists"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        lists = response.json()
        for lst in lists:
            if lst["title"] == "List-AI":
                return lst["_id"]
        print("List-AI not found!")
        return None
    else:
        print("Error fetching lists:", response.text)
        return None


def get_cards(board_id, list_id):
    """
    Fetch all cards from a given board and list.
    """
    url = f"{BASE_URL}/api/boards/{board_id}/lists/{list_id}/cards"
    print(f" Fetching cards from: {url}")

    if not HEADERS.get("Authorization"):
        print("Error: No Authorization token set in headers!")
        return []

    response = requests.get(url, headers=HEADERS)

    #print("Response Status Code:", response.status_code)
    #print("Response Headers:", response.headers)
    #print("Response Content:", response.text)

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Error: Response is not valid JSON. Is the API token correct?")
            return []
    elif response.status_code == 401:
        print("Unauthorized! API token might be expired or invalid.")
        return []
    else:
        print("Error fetching cards:", response.text)
        return []


def fetch_tasks_ai():
    board_id = get_boards(get_api_token(USERNAME, PASSWORD)[0])
    if not board_id:
        return []

    list_id = get_lists(board_id)
    if not list_id:
        return []

    return get_cards(board_id, list_id)  # Return the cards list


def fetch_tasks(board_id, list_id):
    """
    Fetches Wekan tasks for a specific board and list.
    """
    global HEADERS

    if not HEADERS.get("Authorization"):
        print("Re-authenticating: Fetching a new API token...")
        user_id = get_api_token(USERNAME, PASSWORD)[0]
        if not user_id:
            print("Error: Unable to get API token. Exiting...")
            return []

    if not board_id or not list_id:
        print("Error: Missing board_id or list_id!")
        return []

    print(f"Fetching tasks for Board: {board_id}, List: {list_id}")

    tasks = get_cards(board_id, list_id)

    if not tasks:
        print("Error: No tasks found in this list.")

    return tasks


