from typing import List, Optional
from sentence_transformers import SentenceTransformer
from loguru import logger

from tenacity import retry, wait_random_exponential, stop_after_attempt

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_embeddings(texts: List[str], embedding_model: Optional[str]) -> List[List[float]]:
    """
    Embed texts using sbert.

    Args:
        texts: The list of texts to embed.

    Returns:
        A list of embeddings, each of which is a list of floats.

    Raises:
        Exception: If the error.
    """
    if not embedding_model:
        embedding_model = "all-MiniLM-L6-v2"
    model = SentenceTransformer(embedding_model)

    vector = model.encode(texts, show_progress_bar=False).tolist()

    # Return the embeddings as a list of lists of floats
    return vector
