import time
import requests
import json
import asyncio
import aiohttp

import config
import wekan_api


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
    url = f"{wekan_api.BASE_URL}/api/boards/{BOARD_ID}/lists/{LIST_ID}/cards/{card_id}"
    async with session.delete(url, headers=wekan_api.HEADERS) as response:
        if response.status == 200:
            print(f"Deleted card {card_id}")
        else:
            print(f"Failed to delete card {card_id}: {await response.text()}")


def create_card_batch(card_batch, BOARD_ID, LIST_ID, SWIMLANE_ID, USER_ID):
    """
    Creates multiple cards in Wekan using persistent connections (faster).
    Processes a batch at a time to maintain order.
    """

    url = f"{wekan_api.BASE_URL}/api/boards/{BOARD_ID}/lists/{LIST_ID}/cards"

    with requests.Session() as session:
        session.headers.update(wekan_api.HEADERS)

        for card in card_batch:
            payload = {
                "title": card["title"],
                "description": "",
                "authorId": USER_ID,
                "swimlaneId": SWIMLANE_ID
            }

            response = session.post(url, json=payload)

            if response.status_code == 200:
                print(f"Created card '{card['title']}'")
            else:
                print(f"Failed to create card '{card['title']}' : {response.status_code} | {response.text}")

            time.sleep(0.1)  # delay to prevent overwhelming Wekan API


def sort_cards(sorted_titles, cards, BOARD_ID, LIST_ID, CARDS_CREATION_BATCH=config.CARDS_CREATION_BATCH):
    """
    Deletes all existing cards asynchronously and recreates them in batches to speed up the process.
    """

    if isinstance(sorted_titles, str):
        try:
            sorted_titles = json.loads(sorted_titles)
        except json.JSONDecodeError:
            print("Error: `sorted_titles` is not valid JSON.")
            return

    if not isinstance(sorted_titles, list) or not all(
            isinstance(item, dict) and "title" in item for item in sorted_titles):
        print("Error: `sorted_titles` must be a list of dictionaries with a 'title' key.")
        return

    # Delete all cards asynchronously
    print("Deleting cards...")
    asyncio.run(delete_all_cards(cards, BOARD_ID, LIST_ID))

    # Retrieve the swimlane ID safely
    if not cards:
        print("Error: No existing cards to retrieve `swimlaneId` from!")
        return

    SWIMLANE_ID = cards[0]["swimlaneId"]
    USER_ID = wekan_api.get_api_token(wekan_api.USERNAME, wekan_api.PASSWORD)[0]

    # Recreate cards in batches (faster while keeping order)
    # print(f"Recreating {len(sorted_titles)} cards in batches of {CARDS_CREATION_BATCH}...")

    for i in range(0, len(sorted_titles), CARDS_CREATION_BATCH):
        batch = sorted_titles[i:i + CARDS_CREATION_BATCH]
        create_card_batch(batch, BOARD_ID, LIST_ID, SWIMLANE_ID, USER_ID)

    print("Sorting Completed!")
