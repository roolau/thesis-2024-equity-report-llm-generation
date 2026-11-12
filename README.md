# LLM-generated risk sections for equity research reports

> **Archived (spring 2024).** This is the code from my M.Sc. thesis at LUT University. It was written for the GPT-3.5 generation of models and is kept as a record of the work, not maintained. The models it calls have since been superseded or retired, so it will not reproduce the original outputs as-is.

**Thesis:** *Toward algorithm-based sell-side equity analyst storytelling* (LUT University, 2024). <!-- TODO: add the LUTPub / URN link -->

## What it does

The thesis asked whether a large language model can draft the qualitative **risk section** of a sell-side equity research report on a Finnish listed company, using the company's own interim report as source material.

The code compares two ways of adapting GPT-3.5-turbo to this task, alone and combined:

- **Fine-tuning** on 20 examples. Each pairs a request ("write a risk section for company X") with the risk section from a published analyst report on that company.
- **Retrieval-augmented generation (RAG)** over the company's interim report, using a LlamaIndex vector index with a 0.7 similarity cutoff.
- **Few-shot prompting** with two example risk sections.

All prompts and outputs are in **Finnish**. The system prompt (`sysprompt_fi.txt`) casts the model as "Opie", an assistant to equity analysts. It writes 100–150 word risk sections of 2–4 paragraphs, grounded only in the provided documents, without investment advice or unsupported figures.

`evaluation.py` runs four configurations per company:

| # | Model | RAG | Few-shot |
|---|-------|-----|----------|
| 1 | gpt-3.5-turbo | – | – |
| 2 | gpt-3.5-turbo | – | 2 examples |
| 3 | fine-tuned gpt-3.5-turbo | ✓ | – |
| 4 | gpt-3.5-turbo | ✓ | 2 examples |

For each run it records ROUGE-1 F1 and, for the non-RAG runs, output perplexity from the token log-probabilities. Results and their discussion are in the thesis.

## Repository layout

| File | Purpose |
|------|---------|
| `extraction.py` | Text extraction from PDF files or URLs (PyMuPDF) |
| `fine_tuning.py` | Builds the JSONL dataset and optionally submits the OpenAI fine-tuning job |
| `rag.py` | LlamaIndex query engine over the source documents |
| `model.py` | Interactive command-line runner (RAG or single prompt) |
| `evaluation.py` | Runs the four configurations for one company and saves an `.xlsx` |
| `constants.py` | Models, hyperparameters (15 epochs, LR multiplier 2.0, temperature 0.5), paths, training questions |
| `common.py` | System prompt loading and the OpenAI client |
| `sysprompt_fi.txt` | System prompt (Finnish) |
| `data/README.md` | Expected data layout. The data itself is not included. |

## Running it

Requires Python 3.11.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # add OPENAI_API_KEY

python model.py                 # RAG answer for the PDFs you enter
python evaluation.py            # the four configurations for one company
python fine_tuning.py           # build the JSONL files from data/
python fine_tuning.py --submit  # ...and start a fine-tuning job
```

The fine-tuned checkpoint (`ft:gpt-3.5-turbo-0125:personal::…`) belonged to a personal OpenAI account and is not publicly accessible. To run configuration 3, train your own model and set `FINE_TUNED_MODEL_NAME`.

## Data

The training targets are copyrighted analyst reports, so they are not included, and neither are the JSONL files generated from them. See [`data/README.md`](data/README.md) for the layout and the example format. The few-shot examples in `evaluation.py` are fetched from public OP report URLs that may no longer resolve.

## Known limitations

Looking back with more experience, I would do these differently. They are left as they were in the thesis so the code matches what was reported.

- **The validation set duplicates the training set.** `fine_tuning.py` reads validation targets from the training directory, so the validation loss during fine-tuning was not a held-out measure. The validation questions are also paired with training texts.
- **ROUGE is computed against the input, not a reference answer.** `evaluation.py` scores each response against its own prompt plus source documents. The score therefore measures lexical overlap with the source material, a rough groundedness proxy, not similarity to an analyst-written risk section. The prompt differs between configurations (few-shot examples, retrieved chunks), so scores are not strictly comparable across them.
- **Perplexity is only available without RAG**, because the LlamaIndex query engine doesn't expose log-probabilities.
- **Small sample.** 20 fine-tuning examples and a handful of evaluation companies, one run each at temperature 0.5.

## Changes from the original code

These are portability fixes only. Prompts, models, hyperparameters and the evaluation logic are unchanged.

- Replaced hard-coded Windows/OneDrive paths with paths relative to the repository, overridable through `DATA_DIR` and `RESULTS_DIR`.
- Moved the system prompt and OpenAI client into `common.py`. Previously, importing `model.py` or `rag.py` ran dataset generation in `fine_tuning.py` as a side effect.
- Fixed `model.py`, which passed the source tuple to the extractor without unpacking it and crashed when page numbers were left empty.
- Fixed `extraction.py`, which dropped the last page when parsing whole documents. The single-page extraction used in the experiments is unchanged.
- Made the training-file order explicit (case-insensitive, matching Windows) so examples pair with the same questions on every OS.
- Replaced the full Conda environment dump with a minimal `requirements.txt` pinned to the original versions.

## License

Code: MIT (see `LICENSE`). The thesis text and any third-party reports are not covered by this license.
