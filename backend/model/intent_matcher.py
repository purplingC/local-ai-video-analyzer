from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import re


class IntentMatcher:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_dir = Path("models/intent_embed")
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Load SentenceTransformer 
        self.model = SentenceTransformer("models/intent_embed")

        # Define intents with richer coverage
        self.intent_examples = {
            "transcribe": [
                "transcribe the video", "convert audio to text", "speech to text",
                "turn speech into text", "generate subtitles", "caption the video"
            ],
            "detect": [
                "detect objects", "analyze the video", "what objects are shown",
                "identify what's in the video", "run object detection",
                "recognize items", "analyze frames"
            ],
            "generate": [
                "generate a report", "create a summary", "make a pdf report",
                "make a pptx presentation", "summarize the video", "generate output",
                "produce a report", "create powerpoint slides", "make summary",
                "generate documentation", "output pdf or pptx"
            ],
            "clarify": [
                "hello", "hi", "help me", "what can you do", "options", "menu"
            ]
        }

        # Precompute embeddings
        self.embeddings = {
            label: np.mean([self.embed(t) for t in texts], axis=0)
            for label, texts in self.intent_examples.items()
        }

    def embed(self, text: str) -> np.ndarray:
        emb = self.model.encode(text, convert_to_numpy=True)
        return emb.astype(np.float32)

    def normalize_query(self, query: str) -> str:
        q = query.lower().strip()
        q = re.sub(r"[^\w\s]", "", q)  # remove punctuation

        if q in ["generate", "make", "create", "summary", "report"]:
            return "generate a report"
        if q in ["detect", "recognize", "analyze"]:
            return "detect objects in the video"
        if q in ["transcribe", "caption", "subtitles", "speech"]:
            return "transcribe the video"
        return q

    def predict_multiple(self, query, top_k=3):
        qnorm = self.normalize_query(query)
        query_vec = self.embed(qnorm)
        sims = {
            label: float(np.dot(query_vec, ref) /
                         (np.linalg.norm(query_vec) * np.linalg.norm(ref)))
            for label, ref in self.embeddings.items()
        }
        results = sorted(sims.items(), key=lambda x: x[1], reverse=True)
        return results[:top_k]
