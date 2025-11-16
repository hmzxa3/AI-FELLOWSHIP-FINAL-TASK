# ingestion/ingest.py
import os
import argparse
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app")))

from services.retriever import Retriever

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", required=True, help="Directory with documents to ingest")
    parser.add_argument("--chroma", default="./chroma_db", help="Chroma persist directory")
    args = parser.parse_args()

    retr = Retriever(persist_directory=args.chroma)

    for root, _, files in os.walk(args.dir):
        for fn in files:
            path = os.path.join(root, fn)
            try:
                print("Ingesting", path)
                retr.ingest_file(path)
            except Exception as e:
                print("Failed to ingest", path, e)

if __name__ == "__main__":
    main()
