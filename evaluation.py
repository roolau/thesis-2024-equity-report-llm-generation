"""Run the four thesis configurations on one company and save the results.

Configurations (model, RAG, few-shot):
    1. gpt-3.5-turbo,        no RAG, zero-shot
    2. gpt-3.5-turbo,        no RAG, two examples
    3. fine-tuned 3.5-turbo, RAG,    zero-shot
    4. gpt-3.5-turbo,        RAG,    two examples

Usage:
    python evaluation.py   # prompts for report PDFs and the company name
"""
import re

import pandas as pd
from rouge import Rouge

import constants as c
from extraction import extract_texts_from_pdfs
from model import get_sources, get_user_input, use_model
from rag import rag

# Few-shot examples: risk sections from two public OP analyst reports (linked, not redistributed).
# These links worked in 2024 and may no longer resolve.
EXAMPLE_URLS = [
    "https://www.op.fi/documents/20556/64847/Kamux_Q42023.pdf",
    "https://www.op.fi/documents/20556/64847/Nurminen_110324.pdf",
]
EXAMPLE_NAMES = ["Kamux", "Nurminen Logistics"]


def append_to_df(df, company, model, rag, shot, prompt, response, rouge, perplexity):
    new_row = {"company": company, "model": model, "rag": rag, "shot": shot, "prompt": prompt,
               "response": response, "rouge": rouge, "perplexity": perplexity}
    return pd.concat([df, pd.DataFrame.from_records([new_row])])


def score(hyp, ref):
    # NOTE (kept as in the thesis): callers pass the *prompt including the source documents*
    # and the model response, so this ROUGE-1 F1 measures lexical overlap between the output
    # and its input material (a rough groundedness proxy), not similarity to a reference
    # risk section. Because the prompt differs between configurations (few-shot examples,
    # retrieved chunks vs. full sources), scores are not strictly comparable across them.
    rouge_score = Rouge().get_scores(hyp, ref)[0]["rouge-1"]["f"]
    print(f"ROUGE-1 (F1 score): {rouge_score}")
    return rouge_score


if __name__ == "__main__":
    models = ["gpt-3.5-turbo", "gpt-3.5-turbo", c.FINE_TUNED_MODEL_NAME, "gpt-3.5-turbo"]
    use_rag = [0, 0, 1, 1]
    shot = [0, 1, 0, 1]

    results_df = pd.DataFrame(columns=["company", "model", "rag", "shot", "prompt", "response", "rouge", "perplexity"])

    extracted_texts = extract_texts_from_pdfs(*get_sources())

    examples = extract_texts_from_pdfs(EXAMPLE_URLS, 2, 2)
    examples = [re.split(r"\n \n |Vuosittainen liikevaihto", e.split("Riskit")[1])[0].strip() for e in examples]

    final_examples = ""
    for idx, (content, name) in enumerate(zip(examples, EXAMPLE_NAMES), 1):
        final_examples += f"ESIMERKKI {idx}, {name}:\n\n{content}\n\n"

    consolidated_sources = "".join(extracted_texts)

    company = get_user_input()
    prompt = f"Kirjoita lyhyt osio yrityksen {company} keskeisistä riskeistä analyytikkoraporttien mukaisesti."

    c.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(len(models)):
        c.FINE_TUNED_MODEL_NAME = models[i]  # use_model() and rag() read this at call time
        if shot[i] == 1:
            # "Before your task, here are two examples of a well-written risk section whose style
            # and structure you should follow."
            final_prompt = (
                "\n\nEnnen tehtävääsi annan sinulle kaksi esimerkkiä oikeaoppisesta riskit-osiosta "
                "analyysiraportilla, joiden tyylistä ja rakenteesta sinun tulee ottaa mallia."
                f"\n\n{final_examples}\n\n{prompt}"
            )
        else:
            final_prompt = prompt

        if use_rag[i] == 1:
            query_engine = rag(extracted_texts)
            response = query_engine.query(final_prompt).response
            print(response)
            rouge = score(consolidated_sources + final_prompt, response)
            perplexity = None  # logprobs are not exposed through the LlamaIndex query engine
        else:
            # "Use the following review document of {company} as your source:"
            final_prompt += f"Käytä seuraavaa yrityksen {company} katsausdokumenttia analysoitavana tietolähteenäsi:\n\n{consolidated_sources}"
            final_prompt, response, perplexity = use_model(final_prompt)
            rouge = score(final_prompt, response)

        results_df = append_to_df(results_df, company, models[i], use_rag[i], shot[i],
                                  final_prompt, response, rouge, perplexity)
        print(results_df)
        results_df.to_excel(c.RESULTS_DIR / f"results_{company}.xlsx", index=False, engine="openpyxl")
