import os
import faiss
import json
import numpy as np

from typing import Optional, List
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings


# -----------------------------
# CONFIG
# -----------------------------
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
TOP_K = 5


# -----------------------------
# GLOBAL STATE (OK FOR MVP)
# -----------------------------
_embeddings: Optional[OpenAIEmbeddings] = None
_index: Optional[faiss.IndexFlatL2] = None
_chunks: List[str] = []


# -----------------------------
# EMBEDDING MODEL
# -----------------------------
def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY,
        )
    return _embeddings


# -----------------------------
# LOAD INDEX (SAFE)
# -----------------------------
def load_index():
    global _index, _chunks

    index_path = settings.FAISS_INDEX_PATH + ".index"
    chunks_path = settings.FAISS_INDEX_PATH + ".chunks"

    if os.path.exists(index_path) and os.path.exists(chunks_path):
        try:
            _index = faiss.read_index(index_path)

            with open(chunks_path, "r") as f:
                _chunks = json.load(f)

        except Exception as e:
            print("⚠️ FAISS load failed, resetting index:", e)
            _index = None
            _chunks = []


# -----------------------------
# SAVE INDEX
# -----------------------------
def save_index():
    global _index, _chunks

    if _index is None:
        return

    os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)

    faiss.write_index(_index, settings.FAISS_INDEX_PATH + ".index")

    with open(settings.FAISS_INDEX_PATH + ".chunks", "w") as f:
        json.dump(_chunks, f)


# -----------------------------
# ADD DOCUMENT TO RAG
# -----------------------------
async def add_document_to_index(text: str, source: str = "") -> int:
    global _index, _chunks

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = splitter.split_text(text)

    embedder = get_embeddings()
    vectors = await embedder.aembed_documents(chunks)

    matrix = np.array(vectors, dtype="float32")

    # init index if needed
    if _index is None:
        _index = faiss.IndexFlatL2(matrix.shape[1])

    _index.add(matrix)
    _chunks.extend(chunks)

    save_index()

    return len(chunks)


# -----------------------------
# RETRIEVE CONTEXT
# -----------------------------
async def retrieve_relevant_chunks(query: str, top_k: int = TOP_K) -> List[str]:

    if _index is None or len(_chunks) == 0:
        return []

    embedder = get_embeddings()
    q_vector = await embedder.aembed_query(query)

    q_matrix = np.array([q_vector], dtype="float32")

    distances, indices = _index.search(
        q_matrix,
        min(top_k, len(_chunks))
    )

    results = []
    for i in indices[0]:
        if 0 <= i < len(_chunks):
            results.append(_chunks[i])

    return results