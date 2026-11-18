"""
Hybrid Retriever for DarGlobal and Wasalt Real Estate Knowledge Store.
Combines BM25-style frequency scoring, n-gram lexical matching,
and entity-boosted relevance for high-precision retrieval without heavy torch dependencies.
"""

import json
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class RealEstateRetriever:
    def __init__(self, kb_path: Path = None):
        if kb_path is None:
            kb_path = DATA_DIR / "knowledge_base.json"
        self.kb_path = kb_path
        self.documents: List[Dict[str, Any]] = []
        self.doc_tokens: List[List[str]] = []
        self.idf: Dict[str, float] = {}
        self.avg_doc_len: float = 0.0
        self.k1 = 1.5
        self.b = 0.75
        self.load_and_index()

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer that handles English, Arabic, numbers and hyphenated words."""
        cleaned = re.sub(r"[^\w\s\-]", " ", text.lower())
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        return tokens

    def load_and_index(self):
        """Loads knowledge base and builds BM25 index."""
        if not self.kb_path.exists():
            return

        with open(self.kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.documents = data.get("documents", [])

        if not self.documents:
            return

        total_len = 0
        df: Dict[str, int] = {}
        self.doc_tokens = []

        for doc in self.documents:
            # Index title, text, and metadata keywords
            searchable_text = f"{doc.get('title', '')} {doc.get('text', '')}"
            meta = doc.get("metadata", {})
            if isinstance(meta, dict):
                for v in meta.values():
                    if isinstance(v, list):
                        searchable_text += " " + " ".join(str(item) for item in v)
                    elif isinstance(v, str):
                        searchable_text += " " + v

            tokens = self._tokenize(searchable_text)
            self.doc_tokens.append(tokens)
            total_len += len(tokens)

            # Document frequency for IDF
            unique_terms = set(tokens)
            for term in unique_terms:
                df[term] = df.get(term, 0) + 1

        n_docs = len(self.documents)
        self.avg_doc_len = total_len / n_docs if n_docs > 0 else 1.0

        for term, freq in df.items():
            self.idf[term] = math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Scores documents against query and returns top_k results."""
        if not self.documents:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.documents[:top_k]

        scores: List[Tuple[int, float]] = []
        
        # Priority keyword boosts (e.g. brand names and locations)
        high_value_keywords = {
            "pagani", "lamborghini", "missoni", "trump", "elie saab", "versace",
            "dubai", "marbella", "spain", "oman", "muscat", "riyadh", "jeddah",
            "shams", "parisiana", "qasr", "sedra", "infath", "auction", "villa", "penthouse"
        }

        for idx, doc in enumerate(self.documents):
            tokens = self.doc_tokens[idx]
            doc_len = len(tokens)
            score = 0.0

            # Term frequencies
            tf_map: Dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            for q_term in query_tokens:
                if q_term in tf_map:
                    tf = tf_map[q_term]
                    idf_val = self.idf.get(q_term, 0.5)
                    # BM25 formula
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += idf_val * (numerator / denominator)

                    # High-value entity boost
                    if q_term in high_value_keywords:
                        score += 3.0

            # Boost exact substring matches in title or entity
            query_lower = query.lower()
            if query_lower in doc.get("title", "").lower():
                score += 5.0
            if query_lower in doc.get("entity", "").lower():
                score += 3.0

            scores.append((idx, score))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_idx, score in scores[:top_k]:
            doc_copy = dict(self.documents[doc_idx])
            doc_copy["relevance_score"] = round(score, 3)
            results.append(doc_copy)

        return results

if __name__ == "__main__":
    retriever = RealEstateRetriever()
    print(f"Loaded {len(retriever.documents)} docs.")
    test_queries = [
        "Tell me about Pagani residences in Dubai",
        "Lamborghini villas in Spain",
        "Wasalt off plan projects in Riyadh",
        "Aida Oman Trump golf villas",
        "Infath auctions"
    ]
    for q in test_queries:
        res = retriever.retrieve(q, top_k=2)
        print(f"\nQuery: {q}")
        for r in res:
            print(f"  -> [{r['entity']}] {r['title']} (Score: {r['relevance_score']})")
