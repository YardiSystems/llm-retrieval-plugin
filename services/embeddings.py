from typing import List
import os
from services.openai import get_embeddings as openai_get_embeddings
from services.sbert import get_embeddings as sbert_get_embeddings

def get_embeddings(texts: List[str]) -> List[List[float]]:
    embedding_model = os.environ.get("EMBEDDING_MODEL") or "text-embedding-ada-002"
    embeddings = openai_get_embeddings(texts) if embedding_model == "text-embedding-ada-002" else sbert_get_embeddings(texts, embedding_model)
    return embeddings