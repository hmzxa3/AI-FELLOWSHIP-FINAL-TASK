# RealEstateGPT — Quickstart (local)

## Prereqs
- Python 3.10+ (3.11 recommended)
- OpenAI API key
- (Optional) Docker & docker-compose

## Setup (Python local)
1. Clone repo
2. Create venv and install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3. Set env variables (example):
   ```bash
   export OPENAI_API_KEY="sk-..."
   export CHROMA_DIR="./chroma_db"
   export DATA_DIR="./data/uploads"
   export BACKEND_URL="http://localhost:8000"
   ```
4. Ingest PDFs (put PDFs into `./example_pdfs` or any folder):
   ```bash
   python ingestion/ingest.py --dir ./example_pdfs --chroma ./chroma_db
   ```
   Or upload PDFs via Streamlit sidebar after running backend.

5. Run backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

6. Run Streamlit UI (new terminal):
   ```bash
   export BACKEND_URL=http://localhost:8000
   streamlit run frontend/streamlit_app.py
   ```

7. Visit Streamlit in browser (usually http://localhost:8501).

## Docker quickstart
1. Copy `.env.example` -> `.env` and set `OPENAI_API_KEY`.
2. Run:
   ```bash
   docker compose up --build
   ```
3. Backend will be at http://localhost:8000.

## Notes
- This demo uses OpenAI embeddings + ChatOpenAI. Ensure `OPENAI_API_KEY` is present.
- For scanned PDFs, install Tesseract (already in Dockerfile). The retriever currently extracts plain text from PDFs; extend with OCR if pages have images only.
- If you prefer another vector DB (Pinecone/Weaviate), swap `Chroma` usage in `retriever.py`.
