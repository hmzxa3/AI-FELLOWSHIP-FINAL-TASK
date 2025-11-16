# frontend/streamlit_app.py
import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="RealEstateGPT Demo", page_icon="🏡", layout="wide")
st.title("RealEstateGPT — Demo")

with st.sidebar:
    st.header("Upload Documents")
    uploaded_file = st.file_uploader("Upload a PDF or text file to index", type=["pdf", "txt"])
    if uploaded_file is not None:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        try:
            resp = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=120)
            if resp.ok:
                st.success(f"Uploaded & ingested: {uploaded_file.name}")
            else:
                st.error(f"Upload failed: {resp.text}")
        except Exception as e:
            st.error(f"Upload error: {e}")

st.markdown("---")
st.subheader("Ask RealEstateGPT")
query = st.text_input("Type your question about listings, documents, or policies:")

if st.button("Send"):
    if not query:
        st.warning("Please type a question first.")
    else:
        try:
            with st.spinner("Contacting backend..."):
                resp = requests.post(f"{BACKEND_URL}/chat", json={"query": query}, timeout=120)
                if resp.ok:
                    data = resp.json()
                    st.markdown("**Answer:**")
                    st.write(data.get("answer", "No answer returned"))
                    st.markdown("**Sources:**")
                    srcs = data.get("source_documents", [])
                    if srcs:
                        for s in srcs:
                            st.write(s.get("metadata", {}))
                            content = s.get("page_content", "")
                            st.write(content[:1200] + ("..." if len(content) > 1200 else ""))
                    else:
                        st.write("No sources returned.")
                else:
                    st.error(f"Backend returned error: {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
