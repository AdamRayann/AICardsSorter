import unittest
from unittest.mock import patch, MagicMock
import json
import ai_sorter  # Import your module containing the functions

class TestTaskSorting(unittest.TestCase):


    def test_parse_sorted_tasks_valid_json(self):
        """Test if valid JSON is parsed correctly."""
        llama_output = """
        [
            {"_id": "task1", "title": "Task 1", "sort": 0},
            {"_id": "task2", "title": "Task 2", "sort": 1}
        ]
        """
        parsed_tasks = ai_sorter.parse_sorted_tasks(llama_output)

        self.assertEqual(len(parsed_tasks), 2)
        self.assertEqual(parsed_tasks[0]["_id"], "task1")
        self.assertEqual(parsed_tasks[1]["_id"], "task2")

    def test_parse_sorted_tasks_invalid_json(self):
        """Test handling of invalid JSON input."""
        llama_output = """
        [ {"_id": "task1", "title": "Task 1", "sort": 0},
        """
        parsed_tasks = ai_sorter.parse_sorted_tasks(llama_output)

        self.assertEqual(parsed_tasks, [])  # Should return an empty list

    def test_parse_sorted_tasks_cleaning_json_code_blocks(self):
        """Test removal of JSON code block markers from Llama output."""
        llama_output = """
        ```json
        [
            {"_id": "task1", "title": "Task 1", "sort": 0},
            {"_id": "task2", "title": "Task 2", "sort": 1}
        ]
        ```
        """
        parsed_tasks = ai_sorter.parse_sorted_tasks(llama_output)

        self.assertEqual(len(parsed_tasks), 2)
        self.assertEqual(parsed_tasks[0]["_id"], "task1")

    def test_parse_sorted_tasks_empty_response(self):
        """Test handling of empty response."""
        parsed_tasks = ai_sorter.parse_sorted_tasks("[]")
        self.assertEqual(parsed_tasks, [])

if __name__ == "__main__":
    unittest.main()
