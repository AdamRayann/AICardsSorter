import json
import re
import groq

import config


def sort_tasks_with_llama(tasks):
    print("sort_tasks_with_llama started", flush=True)
    """
    Sends a list of tasks to Llama (via Groq API) and retrieves a logically sorted order.
    """
    client = groq.Client(api_key=config.GROQ_API_KEY)

    task_list_str = "\n".join([f"{task['sort']}: {task['title']}" for task in tasks])
    # The following tasks need to be sorted in a logical order based on dependencies, urgency, and best workflow practices:
    # The following tasks need to be sorted in a logical order based on best workflow practices:
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
        # model="llama3-8b-8192,
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



def parse_sorted_tasks(llama_output):
    """
    Parses the AI-generated JSON response and extracts the reordered task list.
    """
    try:
        # print("Raw Llama Output:", llama_output)

        clean_output = re.sub(r"```json|```", "", llama_output).strip()

        if not clean_output or clean_output == "[]":
            return []

        sorted_tasks = json.loads(clean_output)
        return sorted_tasks

    except json.JSONDecodeError:
        print("Error parsing Llama output! Trying fallback method...")
        return []
