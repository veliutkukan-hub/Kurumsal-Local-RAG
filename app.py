import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
import os
import tempfile
from fpdf import FPDF

# Türkçe karakterleri İngilizceye çeviren minik kurtarıcı fonksiyonumuz
def turkce_karakter_temizle(metin):
    ceviriler = {
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C'
    }
    for tr, eng in ceviriler.items():
        metin = metin.replace(tr, eng)
    return metin

st.set_page_config(page_title="Ultimate YBS Asistanı", page_icon="🚀", layout="wide")

# Oturum Yönetimi (Mesajları en üste aldık ki hemen tanısın)
if 'ad' not in st.session_state: st.session_state.ad = ""
if 'soyad' not in st.session_state: st.session_state.soyad = ""
if "messages" not in st.session_state: st.session_state.messages = [] 

with st.sidebar:
    st.header("👤 Kullanıcı Profili")
    st.session_state.ad = st.text_input("Adınız", value=st.session_state.ad)
    st.session_state.soyad = st.text_input("Soyadınız", value=st.session_state.soyad)
    st.markdown("---")
    st.header("📂 Dosya Havuzu")
    yuklenen_dosyalar = st.file_uploader("Belge yükle (PDF/Word)", type=["pdf", "docx"], accept_multiple_files=True)
    st.markdown("---")

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

# 🔥 BUTON MANTIĞINI EN ALTA ALDIK: Cevap biter bitmez anında görünecek!
if len(st.session_state.messages) > 0:
    with st.sidebar:
        st.markdown("### 📊 Raporlama")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Başlığı temizleyip PDF'e yazıyoruz
        baslik = f"Analiz Raporu - {st.session_state.ad} {st.session_state.soyad}"
        temiz_baslik = turkce_karakter_temizle(baslik)
        pdf.cell(200, 10, txt=temiz_baslik, ln=True, align='C')
        
        # Mesajları (Sohbeti) temizleyip PDF'e yazıyoruz
        for msg in st.session_state.messages:
            satir = f"{msg['role'].upper()}: {msg['content']}"
            temiz_satir = turkce_karakter_temizle(satir)
            pdf.multi_cell(0, 10, txt=temiz_satir)
            
        pdf.output("rapor.pdf") 
        
        with open("rapor.pdf", "rb") as pdf_dosyasi:
            PDFbyte = pdf_dosyasi.read()

        st.download_button(
            label="📥 Raporu PDF İndir",
            data=PDFbyte,
            file_name="Kurumsal_Analiz_Raporu.pdf",
            mime="application/octet-stream"
        )