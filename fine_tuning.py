"""Build the fine-tuning dataset and (optionally) submit the OpenAI fine-tuning job.

Usage:
    python fine_tuning.py            # write data/training.jsonl and data/validation.jsonl
    python fine_tuning.py --submit   # ...and create the fine-tuning job
"""
import argparse
import json
import os
import re

import constants as c
from common import SYSTEM_PROMPT, get_client
from extraction import extract_texts_from_pdfs


def extract_risk_section(text):
    # The risk section ("Riskit") sits on page 2 of the analyst reports used as targets.
    return re.split(r"\n \n |Vuosittainen liikevaihto", text.split("Riskit")[1])[0].strip()


def write_jsonl(examples, filename, questions):
    min_length = min(len(examples), len(questions))
    with open(filename, "w", encoding="utf-8") as file:
        for i in range(min_length):
            example_output = extract_risk_section(examples[i])
            file.write(create_example(SYSTEM_PROMPT, questions[i], example_output) + "\n")


def create_example(context, example_questions, example_response):
    json_object = {
        "messages": [
            {"role": "system", "content": f"{context}"},
            {"role": "user", "content": f"{example_questions}"},
            {"role": "assistant", "content": f"{example_response}"},
        ]
    }
    return json.dumps(json_object)


def retrieve_filepaths(directory):  # retrieves the paths of each file in the directory
    # Examples are paired with questions by position, so the order matters. The thesis ran on
    # Windows, where os.scandir returns files case-insensitively sorted; sort the same way
    # explicitly so the pairing (e.g. Harvia before HKScan) is identical on every OS.
    return sorted((entry.path for entry in os.scandir(directory) if entry.is_file()), key=str.lower)


def build_datasets():
    example_outputs_training = extract_texts_from_pdfs(
        retrieve_filepaths(c.TRAINING_OUTPUT_DIRECTORY), 2, 2
    )  # let's use only the second page of the report

    # KNOWN ISSUE (kept as in the thesis run): the validation examples are read from the
    # TRAINING output directory, so the validation set duplicates the training targets and the
    # validation loss reported during fine-tuning is not a held-out measure.
    # The intended line was: retrieve_filepaths(c.VALIDATION_OUTPUT_DIRECTORY)
    example_outputs_validation = extract_texts_from_pdfs(
        retrieve_filepaths(c.TRAINING_OUTPUT_DIRECTORY), 2, 2
    )

    write_jsonl(example_outputs_training, c.TRAINING_FILE_NAME, c.TRAINING_QUESTIONS)
    write_jsonl(example_outputs_validation, c.VALIDATION_FILE_NAME, c.VALIDATION_QUESTIONS)


def upload_file(filename):
    with open(filename, "rb") as f:
        uploaded_file = get_client().files.create(file=f, purpose="fine-tune")
    return uploaded_file.id


def create_fine_tuning_job():
    response = get_client().fine_tuning.jobs.create(
        training_file=upload_file(c.TRAINING_FILE_NAME),
        model=c.MODEL_NAME,
        hyperparameters={
            "n_epochs": c.N_EPOCHS,
            "learning_rate_multiplier": c.LEARNING_RATE,
        },
        validation_file=upload_file(c.VALIDATION_FILE_NAME),
    )
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--submit", action="store_true", help="create the fine-tuning job after building the files")
    args = parser.parse_args()

    build_datasets()
    print(f"Wrote {c.TRAINING_FILE_NAME} and {c.VALIDATION_FILE_NAME}")
    if args.submit:
        print(create_fine_tuning_job())
