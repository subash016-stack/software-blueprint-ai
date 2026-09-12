"""Script to ingest academic software engineering knowledge base into Qdrant vector store."""

import os
import sys

# Ensure repository root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.retriever import load_and_ingest_knowledge_base


def main():
    print("==================================================")
    print(" Software Blueprint AI - Knowledge Ingestion")
    print("==================================================")
    knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))
    print(f"Scanning knowledge directory: {knowledge_dir}")
    
    total_chunks = load_and_ingest_knowledge_base(knowledge_dir)
    print(f"✅ Ingestion complete! Total chunks indexed: {total_chunks}")


if __name__ == "__main__":
    main()
