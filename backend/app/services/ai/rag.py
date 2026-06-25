import os
import faiss
import json
import numpy as np

from typing import Optional, List
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings


# ──────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────
CHUNK_SIZE    = 512
CHUNK_OVERLAP = 64
TOP_K         = 5


# ──────────────────────────────────────────
# GLOBAL STATE
# Each chunk stored as {"text": str, "category": str | None, "source": str}
# ──────────────────────────────────────────
_embeddings: Optional[OpenAIEmbeddings] = None
_index: Optional[faiss.IndexFlatL2]     = None
_chunks: List[dict]                     = []   # was List[str] — now List[dict]


# ──────────────────────────────────────────
# EMBEDDING MODEL
# ──────────────────────────────────────────
def get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY,
        )
    return _embeddings


# ──────────────────────────────────────────
# LOAD INDEX FROM DISK
# ──────────────────────────────────────────
def load_index():
    global _index, _chunks

    index_path  = settings.FAISS_INDEX_PATH + ".index"
    chunks_path = settings.FAISS_INDEX_PATH + ".chunks"

    if os.path.exists(index_path) and os.path.exists(chunks_path):
        try:
            _index = faiss.read_index(index_path)
            with open(chunks_path, "r") as f:
                raw = json.load(f)

            # ── MIGRATION: old format was List[str], new is List[dict] ──
            if raw and isinstance(raw[0], str):
                _chunks = [{"text": c, "category": None, "source": ""} for c in raw]
            else:
                _chunks = raw

        except Exception as e:
            print("⚠️  FAISS load failed, resetting index:", e)
            _index  = None
            _chunks = []


# ──────────────────────────────────────────
# SAVE INDEX TO DISK
# ──────────────────────────────────────────
def save_index():
    global _index, _chunks

    if _index is None:
        return

    os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(_index, settings.FAISS_INDEX_PATH + ".index")

    with open(settings.FAISS_INDEX_PATH + ".chunks", "w") as f:
        json.dump(_chunks, f)


# ──────────────────────────────────────────
# ADD DOCUMENT TO RAG INDEX
# category_tag: one of the EmailCategory values, or None for untagged
# ──────────────────────────────────────────
async def add_document_to_index(
    text: str,
    source: str = "",
    category_tag: Optional[str] = None,
) -> int:
    global _index, _chunks

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    raw_chunks = splitter.split_text(text)

    if not raw_chunks:
        return 0

    embedder = get_embeddings()
    vectors  = await embedder.aembed_documents(raw_chunks)
    matrix   = np.array(vectors, dtype="float32")

    if _index is None:
        _index = faiss.IndexFlatL2(matrix.shape[1])

    _index.add(matrix)

    # Store as dicts with category metadata
    for chunk in raw_chunks:
        _chunks.append({
            "text":     chunk,
            "category": category_tag,
            "source":   source,
        })

    save_index()
    return len(raw_chunks)


# ──────────────────────────────────────────
# RETRIEVE RELEVANT CHUNKS
# category: if provided, ONLY return chunks matching that category
#           (or untagged chunks as fallback)
# ──────────────────────────────────────────
async def retrieve_relevant_chunks(
    query: str,
    top_k: int = TOP_K,
    category: Optional[str] = None,
) -> List[str]:

    if _index is None or len(_chunks) == 0:
        return []

    embedder = get_embeddings()
    q_vector = await embedder.aembed_query(query)
    q_matrix = np.array([q_vector], dtype="float32")

    # Search more candidates than needed so we can filter
    search_k = min(top_k * 4, len(_chunks))
    distances, indices = _index.search(q_matrix, search_k)

    results = []
    for i in indices[0]:
        if not (0 <= i < len(_chunks)):
            continue

        chunk = _chunks[i]

        # ── CATEGORY FILTER (the key fix from audit) ──
        if category is not None:
            chunk_cat = chunk.get("category")
            # accept if chunk matches the category OR chunk has no category tag
            if chunk_cat is not None and chunk_cat != category:
                continue

        results.append(chunk["text"])

        if len(results) >= top_k:
            break

    # If category filter returned nothing, fall back to top-K unfiltered
    if not results and category is not None:
        for i in indices[0]:
            if 0 <= i < len(_chunks):
                results.append(_chunks[i]["text"])
            if len(results) >= top_k:
                break

    return results