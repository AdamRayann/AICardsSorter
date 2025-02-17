from flask import Flask, request, jsonify

import config
import wekan_api
import task_manager
import ai_sorter
from massage_broker import send_to_rabbitmq

app = Flask(__name__)


@app.route('/')
def home():
    return "Hi, there is no GUI here."

@app.route('/api/sorted-tasks', methods=['POST'])
def reorder_wekan_tasks():
    """
    API Endpoint: Accepts a JSON payload of Wekan cards, sorts them using Llama, and returns the updated order.
    """
    try:
        data = request.json
        # print("Received Data:", json.dumps(data, indent=4))

        if not isinstance(data, list) or len(data) == 0:
            return jsonify({"error": "Invalid request format or empty list"}), 400

        llama_output = ai_sorter.sort_tasks_with_llama(data)
        # print("Llama Raw Output:", llama_output)

        sorted_tasks = ai_sorter.parse_sorted_tasks(llama_output)
        # print("Parsed Sorted Tasks:", sorted_tasks)

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
        data = wekan_api.fetch_tasks_ai()  # Fetch Wekan cards from the correct function

        if not isinstance(data, list) or len(data) == 0:
            return jsonify({"error": "No tasks found or invalid format"}), 400

        llama_output = ai_sorter.sort_tasks_with_llama(data)
        sorted_tasks = ai_sorter.parse_sorted_tasks(llama_output)

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
        tasks = wekan_api.fetch_tasks(board_id, list_id)

        if not tasks:
            return jsonify({"error": "No tasks found for this board and list"}), 404

        llama_output = ai_sorter.sort_tasks_with_llama(tasks)

        if config.USE_RMQ:

            for task in tasks:
                send_to_rabbitmq(config.DELETE_QUEUE,
                                 {"card_id": task["_id"], "board_id": board_id, "list_id": list_id})

            swimlane_id = tasks[0]["swimlaneId"]
            user_id = wekan_api.get_api_token(wekan_api.USERNAME, wekan_api.PASSWORD)[0]
            sorted_tasks = ai_sorter.parse_sorted_tasks(llama_output)
            for task in sorted_tasks:
                card_data = {"title": task["title"], "board_id": board_id, "list_id": list_id,
                             "swimlane_id": swimlane_id, "user_id": user_id}
                send_to_rabbitmq(config.CREATE_QUEUE, card_data)


        else:
            task_manager.sort_cards(llama_output, tasks, board_id, list_id)
        sorted_tasks = ai_sorter.parse_sorted_tasks(llama_output)

        return jsonify(sorted_tasks)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
