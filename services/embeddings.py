from typing import List
import os
from services.openai import get_embeddings as openai_get_embeddings
from services.sbert import get_embeddings as sbert_get_embeddings

def get_embeddings(texts: List[str], embedding_model: str = None) -> List[List[float]]:
    
    embedding_model = embedding_model or os.environ.get("EMBEDDING_MODEL") or "text-embedding-ada-002"

    if embedding_model == "text-embedding-ada-002":
        return openai_get_embeddings(texts)
    else:
        return sbert_get_embeddings(texts, embedding_model)
