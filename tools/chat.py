import logging
import openai
import readline
from chat_utils import ask
from env_vars import OPENAI_API_KEY

if __name__ == "__main__":
    while True:
        user_query = input("Enter your question: ")
        openai.api_key = OPENAI_API_KEY
        logging.basicConfig(level=logging.WARNING,
                            format="%(asctime)s %(levelname)s %(message)s")
        print(ask(user_query))