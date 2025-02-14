import json
import re
import time

from fetch_ai_cards import fetch_tasks
from flask import Flask, request, jsonify
import requests
import json
import groq
import asyncio
import aiohttp
import fetch_ai_cards

# Set up your API key
API_KEY = "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"



app = Flask(__name__)


# Groq API Key


def sort_tasks_with_llama(tasks):
    """
    Sends a list of tasks to Llama (via Groq API) and retrieves a logically sorted order.
    """
    client = groq.Client(api_key=API_KEY)

    task_list_str = "\n".join([f"{task['sort']}: {task['title']}" for task in tasks])
    #The following tasks need to be sorted in a logical order based on dependencies, urgency, and best workflow practices:
    #The following tasks need to be sorted in a logical order based on best workflow practices:
    prompt = f"""
    The following tasks need to be sorted in a **logical** order based on:
    - **Best workflow efficiency** 
    - **Urgency** (more urgent tasks first)
    - **Dependencies** (tasks that require others to be completed should come after)
    

    {task_list_str}

    Please return **only** the sorted list as valid JSON in the exact format below:
     
    [
        {{"_id": "...", "title": "...", "sort": 0 ,...}},
        {{"_id": "...", "title": "...", "sort": 1 ,...}},
        {{"_id": "...", "title": "...", "sort": 2 ,...}}...
    ]
     
    just change the order of the tasks ,No additional text or explanations—just valid JSON output.
    """

    completion = client.chat.completions.create(
        #model="llama3-8b-8192,
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
        top_p=1,
        stream=False,
    )

    result = completion.choices[0].message.content.strip()
    print("Llama API Output (Raw):", result)

    return result

# def sort_tasks_with_llama(tasks):
#     """
#     Sends a list of tasks to Llama (via Groq API) and retrieves a logically sorted order.
#     """
#     client = groq.Client(api_key=API_KEY)
#
#     task_list_str = "\n".join([f"{task['sort']}: {task['title']}" for task in tasks])
#     #The following tasks need to be sorted in a logical order based on dependencies, urgency, and best workflow practices:
#
#     prompt = f"""
#     The following tasks need to be sorted in a logical order based on best workflow practices:
#
#     {task_list_str}
#
#     sort the list title by the best workflow practices
#
#     No additional text or explanations.
#     """
#
#     completion = client.chat.completions.create(
#         model="llama3-8b-8192",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.3,
#         max_tokens=1024,
#         top_p=1,
#         stream=False,
#     )
#
#     result = completion.choices[0].message.content.strip()
#     print("Llama API Output (Raw):", result)
#
#     return result


async def delete_all_cards(cards, BOARD_ID, LIST_ID):
    """Delete all cards in the list asynchronously."""
    async with aiohttp.ClientSession() as session:
        if not cards:
            print("No cards found in the list.")
            return

        delete_tasks = [delete_card(session, card["_id"], BOARD_ID, LIST_ID) for card in cards]
        await asyncio.gather(*delete_tasks)


async def delete_card(session, card_id, BOARD_ID, LIST_ID):
    """Asynchronously deletes a card from Wekan."""
    url = f"{fetch_ai_cards.BASE_URL}/api/boards/{BOARD_ID}/lists/{LIST_ID}/cards/{card_id}"
    async with session.delete(url, headers=fetch_ai_cards.HEADERS) as response:
        if response.status == 200:
            print(f"Deleted card {card_id}")
        else:
            print(f"Failed to delete card {card_id}: {await response.text()}")


def create_card_batch(card_batch, BOARD_ID, LIST_ID, SWIMLANE_ID, USER_ID):
    """
    Creates multiple cards in Wekan using persistent connections (faster).
    Processes a batch at a time to maintain order.
    """

    url = f"{fetch_ai_cards.BASE_URL}/api/boards/{BOARD_ID}/lists/{LIST_ID}/cards"

    with requests.Session() as session:  # Use a persistent session for better performance
        session.headers.update(fetch_ai_cards.HEADERS)

        for card in card_batch:
            payload = {
                "title": card["title"],
                "description": "",
                "authorId": USER_ID,
                "swimlaneId": SWIMLANE_ID
            }

            response = session.post(url, json=payload)

            if response.status_code == 200:
                print(f"✅ Created card '{card['title']}'")
            else:
                print(f"❌ Failed to create card '{card['title']}': {response.status_code} | {response.text}")

            time.sleep(0.1)  # Small delay to prevent overwhelming Wekan API


def sort_cards(sorted_titles, cards, BOARD_ID, LIST_ID, batch_size=6):
    """
    Deletes all existing cards asynchronously and recreates them in batches to speed up the process.
    """

    # Ensure `sorted_titles` is a list
    if isinstance(sorted_titles, str):
        try:
            sorted_titles = json.loads(sorted_titles)
        except json.JSONDecodeError:
            print("❌ Error: `sorted_titles` is not valid JSON.")
            return

    if not isinstance(sorted_titles, list) or not all(
            isinstance(item, dict) and "title" in item for item in sorted_titles):
        print("❌ Error: `sorted_titles` must be a list of dictionaries with a 'title' key.")
        return

    # Step 1: Delete all cards asynchronously
    print("🗑️ Deleting existing cards...")
    asyncio.run(delete_all_cards(cards, BOARD_ID, LIST_ID))

    # Step 2: Retrieve the swimlane ID safely
    if not cards:
        print("❌ Error: No existing cards to retrieve `swimlaneId` from!")
        return

    SWIMLANE_ID = cards[0]["swimlaneId"]
    USER_ID = fetch_ai_cards.get_api_token(fetch_ai_cards.USERNAME, fetch_ai_cards.PASSWORD)[0]

    # Step 3: Recreate cards in batches (faster while keeping order)
    print(f"📌 Recreating {len(sorted_titles)} cards in batches of {batch_size}...")

    for i in range(0, len(sorted_titles), batch_size):
        batch = sorted_titles[i:i + batch_size]
        create_card_batch(batch, BOARD_ID, LIST_ID, SWIMLANE_ID, USER_ID)

    print("🎉 Sorting Completed!")


def parse_sorted_tasks(llama_output):
    """
    Parses the AI-generated JSON response and extracts the reordered task list.
    """
    try:
        #print("Raw Llama Output:", llama_output)

        clean_output = re.sub(r"```json|```", "", llama_output).strip()

        if not clean_output or clean_output == "[]":
            return []

        sorted_tasks = json.loads(clean_output)
        return sorted_tasks

    except json.JSONDecodeError:
        print("Error parsing Llama output! Trying fallback method...")
        return []


@app.route('/api/sorted-tasks', methods=['POST'])
def reorder_wekan_tasks():
    """
    API Endpoint: Accepts a JSON payload of Wekan cards, sorts them using Llama, and returns the updated order.
    """
    try:
        data = request.json
        #print("Received Data:", json.dumps(data, indent=4))

        if not isinstance(data, list) or len(data) == 0:
            return jsonify({"error": "Invalid request format or empty list"}), 400

        llama_output = sort_tasks_with_llama(data)
        #print("Llama Raw Output:", llama_output)


        sorted_tasks = parse_sorted_tasks(llama_output)
        #print("Parsed Sorted Tasks:", sorted_tasks)

        return jsonify(sorted_tasks)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/sorted-tasks', methods=['POST'])
def fetch_and_sort_tasks():
    """
    API Endpoint: Fetches tasks from Wekan, sorts them using Llama, and returns the updated order.
    """
    try:
        data = fetch_ai_cards.fetch_tasks_ai()  # Fetch Wekan cards from the correct function

        if not isinstance(data, list) or len(data) == 0:
            return jsonify({"error": "No tasks found or invalid format"}), 400

        llama_output = sort_tasks_with_llama(data)
        sorted_tasks = parse_sorted_tasks(llama_output)

        return jsonify(sorted_tasks)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/api/<board_id>/<list_id>/sorted-tasks', methods=['GET'])
def get_sorted_wekan_tasks(board_id, list_id):
    """
    API Endpoint: Fetches tasks from Wekan for a given board and list,
    sorts them using Llama, and returns the updated order.
    """
    try:
        # Fetch tasks from Wekan using the existing function
        tasks = fetch_tasks(board_id, list_id)

        if not tasks:
            return jsonify({"error": "No tasks found for this board and list"}), 404

        # Sort tasks using Llama (assuming sort_tasks_with_llama is implemented)
        llama_output = sort_tasks_with_llama(tasks)
        sort_cards(llama_output, tasks, board_id, list_id)
        # Parse and format sorted tasks
        sorted_tasks = parse_sorted_tasks(llama_output)

        return jsonify(sorted_tasks)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
