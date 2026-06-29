"""
RAG Agent — embeds dataset/documents → vector store → retrieves context → LLM answer.
Uses sentence-transformers for embeddings (falls back to TF-IDF if not installed).
"""
import os
import numpy as np
import pandas as pd
from typing import Optional
from services.agents.rag.vector_store import VectorStore

_stores: dict[str, VectorStore] = {}


def _get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        return None


def _tfidf_embed(texts: list[str]) -> np.ndarray:
    """Fallback: simple TF-IDF-like bag-of-words embeddings."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(max_features=256)
    return vec.fit_transform(texts).toarray().astype(np.float32)


def index_dataframe(user_id: str, df: pd.DataFrame) -> int:
    """Convert dataframe rows to text chunks and index them."""
    store = VectorStore()
    chunks = []

    # Row-level chunks (sample for large datasets)
    sample = df.head(200)
    for _, row in sample.iterrows():
        text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        chunks.append(text)

    # Column summary chunks
    for col in df.columns:
        if df[col].dtype == object:
            top = df[col].value_counts().head(5).to_dict()
            chunks.append(f"Column {col} top values: {top}")
        else:
            chunks.append(f"Column {col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}, min={df[col].min()}, max={df[col].max()}")

    embedder = _get_embedder()
    if embedder:
        embeddings = embedder.encode(chunks, show_progress_bar=False)
    else:
        embeddings = _tfidf_embed(chunks)

    store.add(chunks, np.array(embeddings, dtype=np.float32))
    _stores[user_id] = store
    return len(chunks)


def query(user_id: str, question: str, api_key: str, top_k: int = 5) -> str:
    """Retrieve relevant context and answer with LLM."""
    store = _stores.get(user_id)
    if not store or len(store) == 0:
        return "No indexed data found. Upload a dataset first."

    embedder = _get_embedder()
    if embedder:
        q_emb = embedder.encode([question])[0]
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(max_features=256)
        all_texts = store.texts + [question]
        matrix = vec.fit_transform(all_texts).toarray()
        q_emb = matrix[-1]

    context_chunks = store.search(np.array(q_emb, dtype=np.float32), top_k=top_k)
    context = "\n".join(context_chunks)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst. Answer questions using only the provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
            temperature=0.1, max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"RAG answer (no LLM): {context[:500]}"


def clear(user_id: str) -> None:
    _stores.pop(user_id, None)
