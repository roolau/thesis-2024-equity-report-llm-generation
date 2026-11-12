# Shared helpers. Split out of fine_tuning.py so that importing the system prompt
# no longer triggers dataset generation as a side effect.
from functools import lru_cache

from dotenv import load_dotenv  # loading environment variables
from openai import OpenAI  # Open AI model API

import constants as c

load_dotenv()


def open_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


SYSTEM_PROMPT = open_file(c.BASE_DIR / "sysprompt_fi.txt")


@lru_cache(maxsize=1)
def get_client():
    # Created on first use, so modules can be imported without an API key.
    return OpenAI()  # API key is loaded automatically from OPENAI_API_KEY
