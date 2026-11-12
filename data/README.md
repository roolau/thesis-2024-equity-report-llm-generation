# Data (not included)

The data used in the thesis is not redistributed here:

- **Targets** (`training/outputs/`): sell-side analyst reports on Finnish listed companies from OP's equity research, published 2020–2024. They are copyrighted by the publisher.
- **Inputs** (`training/inputs/`, `validation/inputs/`): the companies' own interim reports and financial statement releases. These are public and can be downloaded from each company's investor relations site.
- `training.jsonl` / `validation.jsonl` are generated from the targets, so they are excluded as well.

To rerun the pipeline, place your own PDFs here:

```
data/
├── training/
│   ├── inputs/     # company reports (not used by fine_tuning.py, kept for reference)
│   └── outputs/    # analyst reports with a "Riskit" section on page 2
└── validation/
    ├── inputs/
    └── outputs/
```

Each training example pairs one question from `constants.TRAINING_QUESTIONS` with the risk section extracted from the matching analyst report, in alphabetical file order: Aspo, Asuntosalkku, Cargotec, Exel Composites, Fodelia, Fortum, Harvia, HKScan, Kesko, Koskisen, NoHo Partners, Puuilo, Rapala VMC, Revenio, Scanfil, Stora Enso, Talenom, Telia, TietoEVRY, Uponor.

The format of each JSONL line is the standard OpenAI chat fine-tuning format:

```json
{"messages": [
  {"role": "system", "content": "<sysprompt_fi.txt>"},
  {"role": "user", "content": "Tee riskiosio yrityksen Aspo analyytikkoraporttiin, ..."},
  {"role": "assistant", "content": "<risk section text from the analyst report>"}
]}
```
