import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import numpy as np
import requests
 
# --- CONFIG ---
OLLAMA_URL = "http://192.168.5.99:11434/api/generate"
MODEL = "llama3:8b"
 
# === LOAD & VECTORIZE DATASET ===
@st.cache_resource
def load_and_vectorize():
    df = pd.read_csv("dataset.csv")  # Ton dataset préchargé
    df = df.dropna(subset=["message"])  # Nettoyage
 
    # Conversion en string + gestion NaN avant concaténation
    df["text"] = df["signature"].fillna("").astype(str) + " | " + df["message"].fillna("").astype(str)
 
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    vectors = vectorizer.fit_transform(df["text"]).toarray()
 
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
 
    return df, vectorizer, index, vectors
 
df, vectorizer, index, vectors = load_and_vectorize()
 
# === INTERFACE STREAMLIT ===
st.set_page_config(page_title="Assistant SIEM RAG", layout="centered")
st.title("🛡️ Assistant SIEM RAG")
st.markdown("Pose ta question en langage naturel à propos des attaques détectées dans les logs.")
 
user_query = st.text_input("💬 Exemple : *Give me the attack and the most frequent IP, and how I should block this attack*")
 
# === FUNCTION OLLAMA CALL ===
def call_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "temperature": 0.1,
        "max_tokens": 500,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Exception: {str(e)}"
 
# === RETRIEVE CONTEXT & ASK MODEL ===
if user_query:
    st.info("🔍 Recherche des alertes similaires dans le dataset...")
 
    # Vectoriser la requête utilisateur
    query_vec = vectorizer.transform([user_query]).toarray()
    D, I = index.search(query_vec, k=5)  # top 5 similar alerts
 
    context = "\n\n".join(df.iloc[i]["text"] for i in I[0])
 
    prompt = (
        f"You are a cybersecurity analyst. Based on the following logs:\n\n{context}\n\n"
        f"Answer this question:\n{user_query}\n\n"
        f"Respond in clear and professional English, with direct recommendations where applicable."
    )
 
    st.success("✅ Contexte extrait. Envoi au modèle...")
 
    output = call_ollama(prompt)
 
    st.markdown("### 📥 Question posée :")
    st.code(user_query, language="markdown")
 
    st.markdown("### 🤖 Réponse de l'IA :")
    st.markdown(output)
 
    if st.button("📄 Générer le rapport PDF"):
        from fpdf import FPDF
        import tempfile, os
 
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Question:\n{user_query}\n\n")
        pdf.multi_cell(0, 10, f"Réponse:\n{output}")
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp_file.name)
        with open(tmp_file.name, "rb") as f:
            st.download_button("📥 Télécharger le PDF", f, file_name="rapport_siem_rag.pdf")
        os.unlink(tmp_file.name)
