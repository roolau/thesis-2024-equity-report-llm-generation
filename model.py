"""Interactive runner: give one or more company report PDFs, get a risk section back.

Usage:
    python model.py            # RAG over the given reports (default, as in the thesis)
    python model.py --no-rag   # single prompt to the model, with token-limit check
"""
import argparse

import numpy as np
import tiktoken  # token count estimation

import constants as c
from common import SYSTEM_PROMPT, get_client
from extraction import extract_texts_from_pdfs


def get_user_input():
    return input("Enter the name of the company: ")


def _optional_int(prompt):
    value = input(prompt).strip()
    return int(value) if value else None


def get_sources():
    report_uris = []

    while True:
        user_input = input("Enter the URL or file path of a company report in .pdf format (empty to finish): ")
        if user_input:
            report_uris.append(user_input)
        else:
            break

    first_page = _optional_int("Enter the starting page number (press enter to skip): ") or 1
    last_page = _optional_int("Enter the last page number (press enter to skip): ")
    return report_uris, first_page, last_page


def use_model(prompt):
    response = get_client().chat.completions.create(
        model=c.FINE_TUNED_MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=c.MAX_OUTPUT,  # the model will stop generating tokens at this limit
        temperature=c.TEMPERATURE,  # how likely it is that less probable words are used (0-2; higher = more random)
        logprobs=True,  # returns the natural logarithm of each output token's probability
    )
    logprobs = [token.logprob for token in response.choices[0].logprobs.content]
    perplexity = np.exp(-np.mean(logprobs))  # how uncertain the model is of its output (higher = less certain)
    print(f"Response:\n\n{response.choices[0].message.content}\n\nModel: {response.model}\n")
    print(
        f"Tokens used: {response.usage.total_tokens} (total), {response.usage.prompt_tokens} (input), "
        f"{response.usage.completion_tokens} (output)\nPerplexity score: {perplexity:.5e}"
    )
    return prompt, response.choices[0].message.content, perplexity


def menu(use_rag=1):
    from rag import rag  # imported lazily so the non-RAG path does not need LlamaIndex

    while True:
        # extract the unstructured texts of the user
        extracted_texts = extract_texts_from_pdfs(*get_sources())

        company = get_user_input()
        # "Write a short section on the key risks of {company} in the style of analyst reports."
        prompt = f"Kirjoita lyhyt osio yrityksen {company} keskeisistä riskeistä analyytikkoraporttien mukaisesti."

        if use_rag == 1:
            query_engine = rag(extracted_texts)
            response = query_engine.query(prompt)
            print(response)
            return None

        encoding = tiktoken.encoding_for_model(c.MODEL_NAME)
        token_estimate = len(encoding.encode(prompt + SYSTEM_PROMPT))
        if token_estimate > c.TOKEN_LIMIT * 0.95:
            print("The data you provided exceeds the token limit. Try again.")
            continue

        return use_model(prompt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-rag", action="store_true")
    args = parser.parse_args()
    menu(use_rag=0 if args.no_rag else 1)
