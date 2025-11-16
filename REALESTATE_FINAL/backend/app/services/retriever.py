# backend/app/services/retriever.py
import os
from typing import List, Optional
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

class Retriever:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "realestate_docs"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        os.makedirs(self.persist_directory, exist_ok=True)

        # Embeddings (requires OPENAI_API_KEY)
        self.embedder = OpenAIEmbeddings()

        # Vector DB (Chroma) via LangChain wrapper
        self.vectordb = Chroma(
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
            embedding_function=self.embedder
        )

        # Text splitter for ingestion
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)

        # LLM for generation (ChatOpenAI wrapper)
        self.llm = ChatOpenAI(temperature=0)

        # Retriever and chain
        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 5})
        self.chain = ConversationalRetrievalChain.from_llm(self.llm, self.retriever)

    def _extract_text_from_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages)

    def ingest_file(self, path: str, metadata: Optional[dict] = None):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            text = self._extract_text_from_pdf(path)
        else:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                text = ""

        if not text or text.strip() == "":
            return

        docs = self.text_splitter.split_text(text)
        ids = [f"{os.path.basename(path)}_{i}" for i in range(len(docs))]
        metadatas = [{"source": os.path.basename(path), "chunk": i} for i in range(len(docs))]

        try:
            self.vectordb.add_documents(documents=docs, metadatas=metadatas, ids=ids)
        except Exception:
            if hasattr(self.vectordb, "add_texts"):
                self.vectordb.add_texts(texts=docs, metadatas=metadatas, ids=ids)
            else:
                raise

        try:
            self.vectordb.persist()
        except Exception:
            pass

    def query(self, q: str, k: int = 5) -> List[dict]:
        results = self.retriever.get_relevant_documents(q)
        out = []
        for d in results:
            out.append({
                "page_content": d.page_content,
                "metadata": getattr(d, "metadata", {})
            })
        return out

    def answer(self, question: str):
        res = self.chain({"question": question, "chat_history": []})
        return {
            "answer": res.get("answer"),
            "source_documents": [
                {"page_content": sd.page_content, "metadata": getattr(sd, "metadata", {})}
                for sd in res.get("source_documents", []) or []
            ],
        }
