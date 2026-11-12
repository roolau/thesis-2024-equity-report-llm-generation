import logging
import sys

from llama_index.core import Document, VectorStoreIndex, get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI

import constants as c
from common import SYSTEM_PROMPT

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def rag(texts):
    documents = [Document(text=t) for t in texts]

    logging.info("Creating vector store")
    index = VectorStoreIndex.from_documents(documents)  # LlamaIndex default OpenAI embeddings

    # c.FINE_TUNED_MODEL_NAME is read at call time because evaluation.py swaps it per configuration
    model = OpenAI(model=c.FINE_TUNED_MODEL_NAME, temperature=c.TEMPERATURE, system_prompt=SYSTEM_PROMPT)

    retriever = index.as_retriever()

    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=get_response_synthesizer(llm=model),
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
    )

    return query_engine
