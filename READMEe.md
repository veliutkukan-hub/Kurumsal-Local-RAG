# 🏢 Kurumsal Yerel RAG (Retrieval-Augmented Generation) Asistanı

Bu proje, veri gizliliğinin en üst düzeyde olduğu kurumsal şirketler (bankalar, sağlık kurumları vb.) için tasarlanmış **%100 yerel (offline)** çalışan bir yapay zeka asistanıdır. Veriler hiçbir bulut sunucusuna (OpenAI, Google vb.) gönderilmez.

---

## 📺 Proje Demo Videosu

Sistemin nasıl çalıştığını, kaputun altındaki mimariyi ve bu süreçteki mühendislik kazanımlarımı anlattığım 2 dakikalık uygulamalı demo videomu aşağıdan izleyebilirsiniz:

**[👉 Proje Demo Videosunu İzlemek İçin Tıklayın](https://www.youtube.com/watch?v=S6OprGvsrG4)**

---

## 🚀 Proje Vizyonu ve Özellikler

* **Çoklu Belge Analizi (Multi-Doc):** Aynı anda birden fazla PDF ve Word belgesi yüklenebilir ve çapraz analiz yapılabilir.
* **Sürekli Hafıza (Memory):** Kullanıcı ile yapılan önceki sohbetleri bağlam (context) olarak hatırlar.
* **Kaynak Gösterme (Citation):** Halüsinasyon riskini sıfıra indirmek için cevapların altına belgeden kaynak belirtir.
* **Raporlama:** Analiz sonuçlarını tek tıkla PDF olarak dışa aktarır.
* **Kişiselleştirme:** Kullanıcı profili (Ad-Soyad) ile özelleştirilmiş deneyim sunar.

---

## ⚙️ Kullanılan Teknolojiler (Sistem Mimarisi)

* **Arayüz (UI):** Streamlit
* **Orkestrasyon:** LangChain
* **Vektör Veritabanı:** ChromaDB
* **Gömme (Embedding) Modeli:** Nomic-Embed-Text (Ollama)
* **Büyük Dil Modeli (LLM):** LLaMA 3 (Ollama)

---

## 👨‍💻 Geliştirici

**Utkukan** - *Yönetim Bilişim Sistemleri (YBS)* Bu proje, Microsoft Yaz Okulu 2026 kapsamında "Azure Foundry Local LLM" konseptine alternatif, tamamen yerel bir RAG mimarisi vizyonuyla geliştirilmiştir.
