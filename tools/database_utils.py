import os
import readline
import requests
import sys
from env_vars import BEARER_TOKEN
from typing import Any, Dict


SEARCH_TOP_K = 3


def upsert_files(directory: str):
    """
    Upload all files under a directory to the vector database.
    """
    url = "http://0.0.0.0:8000/upsert-file"
    headers = {"Authorization": "Bearer " + BEARER_TOKEN}
    files = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as f:
                file_content = f.read()
                files.append(("file", (filename, file_content, "text/plain")))
            response = requests.post(url,
                                     headers=headers,
                                     files=files,
                                     timeout=600)
            if response.status_code == 200:
                print(filename + " uploaded successfully.")
            else:
                print(
                    f"Error: {response.status_code} {response.content} for uploading "
                    + filename)


def upsert(id: str, content: str):
    """
    Upload one piece of text to the database.
    """
    url = "http://0.0.0.0:8000/upsert"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + BEARER_TOKEN,
    }

    data = {
        "documents": [{
            "id": id,
            "text": content,
        }]
    }
    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        print("uploaded successfully.")
    else:
        print(f"Error: {response.status_code} {response.content}")


def query_database(query_prompt: str) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input question.
    """
    url = "http://0.0.0.0:8000/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    data = {"queries": [{"query": query_prompt, "top_k": SEARCH_TOP_K}]}

    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        if sys.argv[1] == "upsert_files":
            if len(sys.argv) == 2:
                upsert_files(sys.argv[1])
                exit(0)
            else:
                print("Usage: upsert_files <directory path>")
                exit(0)
        elif sys.argv[1] == "upsert":
            if len(sys.argv) == 4:
                upsert(sys.argv[2], sys.argv[3])
                exit(0)
            else:
                print("Usage: upsert <id> <string>")
                exit(0)
        elif sys.argv[1] == "query_db":
            if len(sys.argv) == 3:
                if sys.argv[2].isdigit():
                    SEARCH_TOP_K = int(sys.argv[2])
            query = input("Enter text to search for: ")
            print(query_database(query))

    print("Usage: upsert_files <directory path> | upsert <id> <string> | query_db [top_k]")
            