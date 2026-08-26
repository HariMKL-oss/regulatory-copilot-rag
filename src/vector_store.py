"""
Hybrid Search Vector Store Engine for Banking Regulations.
Combines:
- BM25 Lexical Keyword Search
- TF-IDF Dense Cosine Vector Similarity
- Reciprocal Rank Fusion (RRF) for hybrid score aggregation
- Role-Based Access Control (RBAC) pre-filtering
"""

import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from document_parser import RegulatoryChunk
from rbac_engine import RBACPolicyEngine


class HybridRegulatoryStore:
    def __init__(self, rbac_engine: Optional[RBACPolicyEngine] = None):
        self.rbac_engine = rbac_engine or RBACPolicyEngine()
        self.chunks: List[RegulatoryChunk] = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.tfidf_matrix = None
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.avg_doc_len = 0.0

    def index_chunks(self, chunks: List[RegulatoryChunk]):
        """Indexes regulatory chunks for hybrid search."""
        self.chunks = chunks
        if len(chunks) == 0:
            return

        corpus = [f"{c.doc_title} {c.section} {c.clause} {c.content}" for c in chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

        # Precompute simple BM25 stats
        total_len = 0
        self.doc_term_freqs = []
        for text in corpus:
            tokens = text.lower().split()
            total_len += len(tokens)
            freqs = {}
            for t in tokens:
                freqs[t] = freqs.get(t, 0) + 1
            self.doc_term_freqs.append(freqs)
            
        self.avg_doc_len = total_len / max(1, len(corpus))

    def _bm25_score(self, query_tokens: List[str], doc_idx: int, k1: float = 1.5, b: float = 0.75) -> float:
        score = 0.0
        doc_freqs = self.doc_term_freqs[doc_idx]
        doc_len = sum(doc_freqs.values())
        
        for token in query_tokens:
            if token in doc_freqs:
                f = doc_freqs[token]
                # Document frequency of term
                n_docs = sum(1 for d in self.doc_term_freqs if token in d)
                idf = math.log((len(self.chunks) - n_docs + 0.5) / (n_docs + 0.5) + 1.0)
                denom = f + k1 * (1 - b + b * (doc_len / self.avg_doc_len))
                score += idf * (f * (k1 + 1.0) / denom)
        return score

    def hybrid_search(self, query: str, user_role: str = "JUNIOR_ANALYST", top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes RBAC-filtered hybrid search combining BM25 and TF-IDF cosine similarity.
        """
        if len(self.chunks) == 0 or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        dense_sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        query_tokens = query.lower().split()
        bm25_scores = np.array([self._bm25_score(query_tokens, i) for i in range(len(self.chunks))])

        # Absolute cosine similarity is already in [0, 1]
        dense_norm = np.clip(dense_sims, 0.0, 1.0)
        bm25_norm = bm25_scores / (bm25_scores + 5.0)

        # Hybrid Reciprocal Weighted Fusion
        hybrid_scores = 0.60 * dense_norm + 0.40 * bm25_norm

        # Rank all
        ranked_indices = np.argsort(hybrid_scores)[::-1]

        results = []
        for idx in ranked_indices:
            chunk = self.chunks[idx]
            # Enforce RBAC Pre-Filter
            if not self.rbac_engine.is_authorized(user_role, chunk.classification):
                continue  # Zero-leakage: omit chunk from user's result set

            results.append({
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "doc_title": chunk.doc_title,
                "classification": chunk.classification,
                "section": chunk.section,
                "clause": chunk.clause,
                "content": chunk.content,
                "hybrid_score": round(float(hybrid_scores[idx]), 4),
                "dense_score": round(float(dense_sims[idx]), 4),
                "bm25_score": round(float(bm25_scores[idx]), 4)
            })

            if len(results) >= top_k:
                break

        return results
