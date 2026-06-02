#!/usr/bin/env python3
"""Pre-download the SentenceTransformer embedding model to cache dir."""
import os
import sys

MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CACHE_DIR = os.getenv("EMBEDDING_CACHE_DIR", "./model_cache")

print(f"Downloading model '{MODEL}' to '{CACHE_DIR}' ...")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(MODEL, cache_folder=CACHE_DIR)
print("Done.")
