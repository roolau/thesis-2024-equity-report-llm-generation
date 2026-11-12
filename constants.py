# Configuration for the thesis experiments (spring 2024).
# Model names and hyperparameters are kept exactly as used in the thesis.
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
RESULTS_DIR = Path(os.getenv("RESULTS_DIR", BASE_DIR / "results"))

# -- MODEL USAGE
MODEL_NAME = "gpt-3.5-turbo"
TOKEN_LIMIT = 16385
MAX_OUTPUT = 300
TEMPERATURE = 0.5  # try also 0.5, 0.3 and 0.1, default is 1
# Embeddings: the RAG pipeline used LlamaIndex's default OpenAI embedding model
# (an earlier version of this file defined text-embedding-3-small, but it was never wired in).

# -- FINE TUNING
# The fine-tuned checkpoint belonged to a personal OpenAI account and is not publicly accessible.
# Override with the FINE_TUNED_MODEL_NAME environment variable to use your own.
FINE_TUNED_MODEL_NAME = os.getenv(
    "FINE_TUNED_MODEL_NAME", "ft:gpt-3.5-turbo-0125:personal::9MyFJkz3:ckpt-step-260"
)
N_EPOCHS = 15
LEARNING_RATE = 2.0  # try with 1.5, 2 and 2.5
TRAINING_INPUT_DIRECTORY = DATA_DIR / "training" / "inputs"
TRAINING_OUTPUT_DIRECTORY = DATA_DIR / "training" / "outputs"
TRAINING_FILE_NAME = DATA_DIR / "training.jsonl"
VALIDATION_INPUT_DIRECTORY = DATA_DIR / "validation" / "inputs"
VALIDATION_OUTPUT_DIRECTORY = DATA_DIR / "validation" / "outputs"
VALIDATION_FILE_NAME = DATA_DIR / "validation.jsonl"

VALIDATION_QUESTIONS = [
    "Ole hyvä ja laadi yksityiskohtainen riskianalyysiosio yritykselle Atria analyytikkoraporttiin",
    "Muotoile osio yrityksen Kempower merkittävistä riskeistä analyytikkoraporttiin liitettäväksi.",
    "Tarvitsen kattavan luettelon yrityksen Modulight riskeistä analyytikkoraportissa.",
    "Muotoile osio yrityksen Sampo merkittävistä riskeistä analyytikkoraporttiin liitettäväksi.",
    "Kehitä keskustelu yrityksen Wetteri kriittisistä riskeistä analyytikkoraportin kontekstissa.",
]

TRAINING_QUESTIONS = [
    "Tee riskiosio yrityksen Aspo analyytikkoraporttiin, korostaen potentiaalisia riskejä.",
    "Rakenna riskiprofiili yritykselle Asuntosalkkusisällytettäväksi analyytikkoraporttiin.",
    "Voisitko tuottaa raportin, joka käsittelee yrityksen Cargotec riskejä.",
    "Haluaisin yhteenvedon yrityksen Exel Composites keskeisistä riskeistä analyytikkoraportin muodossa.",
    "Kehitä keskustelu yrityksen Fodelia keskeisistä riskeistä analyytikkoraportissa.",
    "Voisitko luoda osion, joka keskittyy yrityksen Fortum mahdollisiin vaaroihin ja uhkiin analyytikkoraportin muodossa",
    "Tuota osio, joka keskittyy yrityksen Harvia merkittäviin riskeihin analyytikkoraportissa.",
    "Muodosta yksityiskohtainen riskianalyysi yritykselle HKScan analyytikkoraportin kontekstissa.",
    "Luo riskikeskustelu yritykselle Kesko analyytikkoraportissa korostaen epävarmuustekijöitä.",
    "Tuota yksityiskohtainen analyysi yrityksen Koskisen kriittisistä riskeistä analyytikkoraporttiin.",
    "Rakenna riskiprofiili yritykselle NoHo Partners sisällytettäväksi analyytikkoraporttiin.",
    "Kirjoita osio, joka hahmottelee yrityksen Puuilo keskeiset riskit analyytikkoraportissa.",
    "Laadi osio, joka hahmottelee yrityksen Rapala VMC merkittävät riskit analyytikkoraportissa.",
    "Tuota riskiosio, joka yksityiskohtaisesti kuvailee mahdolliset epävarmuustekijät yritykselle Revenio analyytikkoraportissa.",
    "Laadi raportti, joka keskittyy yrityksen Scanfil kohtaamiin potentiaalisiin riskeihin.",
    "Syntetisoi yrityksen Stora Enso pääasialliset riskitekijät analyytikkoraportin osioon.",
    "Laadi riskien yleiskatsaus yritykselle Talenom analyytikkoraporttiin.",
    "Voisitko syntetisoida yrityksen Telia pääasialliset riskitekijät analyytikkoraportin riskiosioon?",
    "Generoi analyysi yrityksen TietoEVRY keskeisistä riskitekijöistä analyytikkoraportissa.",
    "Kokoa riskiprofiili yritykselle Uponor sisällytettäväksi analyytikkoraporttiin.",
]
