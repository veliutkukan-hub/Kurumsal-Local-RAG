import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
import os
import tempfile
from fpdf import FPDF

st.set_page_config(page_title="Ultimate YBS Asistanı", page_icon="🚀", layout="wide")

# Oturum Yönetimi
if 'ad' not in st.session_state: st.session_state.ad = ""
if 'soyad' not in st.session_state: st.session_state.soyad = ""

with st.sidebar:
    st.header("👤 Kullanıcı Profili")
    st.session_state.ad = st.text_input("Adınız", value=st.session_state.ad)
    st.session_state.soyad = st.text_input("Soyadınız", value=st.session_state.soyad)
    st.markdown("---")
    st.header("📂 Dosya Havuzu")
    yuklenen_dosyalar = st.file_uploader("Belge yükle (PDF/Word)", type=["pdf", "docx"], accept_multiple_files=True)
    st.markdown("---")
    if st.button("Raporu PDF İndir"):
        if "messages" in st.session_state:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Analiz Raporu - {st.session_state.ad} {st.session_state.soyad}", ln=True, align='C')
            for msg in st.session_state.messages:
                pdf.multi_cell(0, 10, txt=f"{msg['role'].upper()}: {msg['content']}")
            pdf.output("rapor.pdf")
            st.success("rapor.pdf oluşturuldu!")

@st.cache_resource
def setup_rag(dosya_listesi):
    tum_dokumanlar = []
    for dosya in dosya_listesi:
        ext = os.path.splitext(dosya.name)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
            t.write(dosya.read())
            path = t.name
        loader = PyPDFLoader(path) if ext == ".pdf" else Docx2txtLoader(path)
        tum_dokumanlar.extend(loader.load())
        os.remove(path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    splits = text_splitter.split_documents(tum_dokumanlar)
    vectorstore = Chroma.from_documents(documents=splits, embedding=OllamaEmbeddings(model="nomic-embed-text"))
    
    # KAYNAK GÖSTERME (Retriever)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever, OllamaLLM(model="llama3")

if yuklenen_dosyalar:
    retriever, llm = setup_rag(yuklenen_dosyalar)
    
    if "messages" not in st.session_state: st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Sorunuz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # RAG Pipeline
        docs = retriever.invoke(prompt)
        context = "\n\n".join([d.page_content for d in docs])
        kaynaklar = "\n".join([f"- {d.metadata.get('source', 'Bilinmeyen Kaynak')}" for d in docs])
        
        template = f"Sen {st.session_state.ad} {st.session_state.soyad} için asistansın. Bağlam: {context} \n Soru: {prompt} \n Cevap (Kaynakları belirt):"
        cevap = llm.invoke(template) + f"\n\n**Kaynaklar:**\n{kaynaklar}"
        
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
else:
    st.info("👈 Belgeleri yükle ve sohbete başla.")