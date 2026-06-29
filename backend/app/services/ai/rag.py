import json
import uuid

from typing import Optional, List
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from app.core.config import settings


# ──────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────
CHUNK_SIZE    = 512
CHUNK_OVERLAP = 64
TOP_K         = 5

# Categories that should NEVER retrieve KB chunks.
# Even if called by mistake, zero chunks returned = zero tokens wasted.
SKIP_RAG_CATEGORIES = {"spam"}


# ──────────────────────────────────────────
# GLOBAL STATE
# ──────────────────────────────────────────
_embeddings: Optional[OpenAIEmbeddings] = None
_pinecone_index = None


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
# GET PINECONE INDEX
# ──────────────────────────────────────────
def get_pinecone_index():
    global _pinecone_index
    if _pinecone_index is None:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        _pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)
    return _pinecone_index


# ──────────────────────────────────────────
# LOAD INDEX — no-op for Pinecone
# Kept for backward compat with main.py lifespan
# ──────────────────────────────────────────
def load_index():
    """No-op — Pinecone is cloud-persistent, nothing to load from disk."""
    try:
        idx = get_pinecone_index()
        stats = idx.describe_index_stats()
        print(f"✓ Pinecone index connected: {stats.total_vector_count} vectors")
    except Exception as e:
        print(f"⚠️  Pinecone connection warning: {e}")


# ──────────────────────────────────────────
# SAVE INDEX — no-op for Pinecone
# Kept for backward compat
# ──────────────────────────────────────────
def save_index():
    """No-op — Pinecone handles persistence automatically."""
    pass


# ──────────────────────────────────────────
# ADD DOCUMENT TO PINECONE INDEX
# ──────────────────────────────────────────
async def add_document_to_index(
    text: str,
    source: str = "",
    category_tag: Optional[str] = None,
) -> int:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    raw_chunks = splitter.split_text(text)

    if not raw_chunks:
        return 0

    embedder = get_embeddings()
    vectors  = await embedder.aembed_documents(raw_chunks)

    idx = get_pinecone_index()

    # Build upsert batch
    batch = []
    for chunk, vector in zip(raw_chunks, vectors):
        batch.append({
            "id":     str(uuid.uuid4()),
            "values": vector,
            "metadata": {
                "text":     chunk,
                "category": category_tag or "",
                "source":   source,
            }
        })

    # Upsert in batches of 100 (Pinecone limit)
    batch_size = 100
    for i in range(0, len(batch), batch_size):
        idx.upsert(vectors=batch[i:i + batch_size])

    print(f"✓ Pinecone: upserted {len(batch)} vectors (source={source}, category={category_tag})")
    return len(raw_chunks)


# ──────────────────────────────────────────
# RETRIEVE RELEVANT CHUNKS
# ──────────────────────────────────────────
async def retrieve_relevant_chunks(
    query: str,
    top_k: int = TOP_K,
    category: Optional[str] = None,
) -> List[str]:

    # ── GUARD: spam aur skip categories ke liye kuch retrieve mat karo ──
    # Primary protection is in ai_processor.py (early exit before generate_reply).
    # This is a second layer — even if called by mistake, returns empty list.
    if category in SKIP_RAG_CATEGORIES:
        print(f"[RAG] Category '{category}' is in SKIP_RAG_CATEGORIES — retrieval blocked ✋")
        return []

    try:
        embedder = get_embeddings()
        q_vector = await embedder.aembed_query(query)

        idx = get_pinecone_index()

        # ── CATEGORY FILTER ──
        query_filter = None
        if category:
            query_filter = {"category": {"$eq": category}}

        results = idx.query(
            vector=q_vector,
            top_k=top_k,
            include_metadata=True,
            filter=query_filter,
        )

        chunks = [
            match["metadata"]["text"]
            for match in results["matches"]
            if "text" in match.get("metadata", {})
        ]

        # ── FALLBACK: agar category filter se kuch nahi mila ──
        # Note: spam yahan kabhi nahi pahunchega (guard upar hai)
        if not chunks and category:
            print(f"[RAG] No chunks found for category='{category}' — falling back to unfiltered top-{top_k}")
            results = idx.query(
                vector=q_vector,
                top_k=top_k,
                include_metadata=True,
            )
            chunks = [
                match["metadata"]["text"]
                for match in results["matches"]
                if "text" in match.get("metadata", {})
            ]

        return chunks

    except Exception as e:
        print(f"⚠️  Pinecone retrieve error: {e}")
        return []