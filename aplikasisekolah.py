import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import markdown
from htmldocx import HtmlToDocx

# =====================================
# 1. KONFIGURASI HALAMAN (TEMA PRO)
# =====================================
st.set_page_config(page_title="APLIKASI MODUL AJAR AI", page_icon="🎓", layout="centered")

# =====================================
# 2. STYLE PRO & BACKGROUND
# =====================================
st.markdown("""
<style>
.stApp {
    background-image: linear-gradient(to right top, #051937, #004d7a, #008793, #00bf72, #a8eb12);
}
.block-container{
    background: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
h1 { color: #004d7a; font-weight: bold; }
.stButton>button {
    background-color: #004d7a;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    height: 60px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# 3. FUNGSI WORD (FORMAT TABEL RAPI)
# =====================================
def create_docx(hasil_ai, data):
    doc = Document()
    # Header Dokumen
    header = doc.add_heading(f"MODUL AJAR AI: {data['mapel']}", 0)
    header.alignment = 1 # Center

    # Tabel Identitas
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    
    table.rows[0].cells[0].text = "Nama Sekolah"
    table.rows[0].cells[1].text = data["sekolah"]
    table.rows[1].cells[0].text = "Mata Pelajaran"
    table.rows[1].cells[1].text = data["mapel"]
    table.rows[2].cells[0].text = "Kelas / Fase"
    table.rows[2].cells[1].text = data["kelas"]
    table.rows[3].cells[0].text = "Materi Pokok"
    table.rows[3].cells[1].text = data["materi"]

    doc.add_paragraph('\n')
    
    # Membersihkan Markdown
    clean_text = hasil_ai.replace("```markdown", "").replace("```", "")
    
    # Convert ke Word
    html_text = markdown.markdown(clean_text, extensions=['tables'])
    new_parser = HtmlToDocx()
    new_parser.add_html_to_document(html_text, doc)

    bio = BytesIO()
    doc.save(bio)
    return bio

# =====================================
# 4. TAMPILAN UTAMA (FORM LENGKAP)
# =====================================
st.title("🎓 APLIKASI MODUL AJAR AI")
st.markdown("“Transformasi Modul Ajar Berbasis Kecerdasan Buatan”")
st.caption("Fitur: ATP + Blueprint Soal + PG Kompleks + Diferensiasi + Rubrik")
st.divider()

# --- INPUT API KEY ---
with st.sidebar:
    st.header("🔐 Kunci Akses")
    api_key_input = st.text_input("Tempel API Key Gemini:", type="password")
    st.info("Mode: Auto-Detect (Kompatibel Semua Laptop)")

# --- INPUT DATA SEKOLAH ---
col1, col2 = st.columns(2)
with col1:
    sekolah = st.text_input("Nama Sekolah", placeholder="SMK Bisa Hebat")
    kelas = st.text_input("Kelas / Fase", placeholder="XI / Fase F")
with col2:
    mapel = st.text_input("Mata Pelajaran", placeholder="Produktif TKJ / Matematika")
    materi = st.text_input("Materi Pokok", placeholder="Fiber Optik / Peluang")

col3, col4 = st.columns(2)
with col3:
    model_belajar = st.selectbox("Model Pembelajaran", 
                                ["Project Based Learning (PjBL)", 
                                 "Problem Based Learning (PBL)", 
                                 "Discovery Learning",
                                 "Teaching Factory (TeFa)"])
with col4:
    mode_soal = st.selectbox("Jenis Soal", ["HOTS - Analisis Kasus", "HOTS - Perhitungan", "Studi Kasus Industri"])

murid = st.text_area("Kondisi & Karakteristik Murid (Untuk Diferensiasi)", 
                     placeholder="Contoh: 20% mahir praktik, 50% rata-rata, 30% butuh bimbingan konsep dasar.",
                     height=100)

# =====================================
# 5. LOGIKA GENERATE (PRO PROMPT + AUTO DETECT)
# =====================================
if st.button("✨ GENERATE MODUL SUPER LENGKAP", type="primary", use_container_width=True):
    
    if not api_key_input:
        st.error("⚠️ API Key wajib diisi di menu samping!")
        st.stop()

    if not sekolah or not mapel:
        st.warning("⚠️ Data Sekolah dan Mapel wajib diisi.")
        st.stop()

    try:
        # 1. Konfigurasi Key
        genai.configure(api_key=api_key_input)
        
        # 2. AUTO-DETECT MODEL (Supaya tidak error 404)
        found_model = "models/gemini-pro" # Default aman
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'gemini' in m.name:
                        found_model = m.name
                        break
        except:
            pass

        st.toast(f"✅ Mesin AI Siap: {found_model}")
        model = genai.GenerativeModel(found_model)
        
        # 3. PROMPT SUPER PRO (Sesuai permintaan Anda)
        prompt = f"""
        Berperanlah sebagai Konsultan Kurikulum SMK & Guru Ahli.
        
        TUGAS:
        Buatkan MODUL AJAR LENGKAP & PERANGKAT PEMBELAJARAN untuk:
        - Sekolah: {sekolah}
        - Kelas: {kelas}
        - Mapel: {mapel}
        - Materi: {materi}
        - Model: {model_belajar}
        - Kondisi Murid: {murid}
        
        WAJIB HASILKAN OUTPUT DALAM FORMAT TABEL MARKDOWN YANG RAPI:
        
        BAGIAN 1: INFORMASI UMUM
        - Identitas Modul
        - Profil Pelajar Pancasila (Pilih yang relevan)
        - Sarana & Prasarana
        - Target Peserta Didik (Berdasarkan kondisi: {murid})
        
        BAGIAN 2: KOMPONEN INTI
        - Tujuan Pembelajaran (ABCD) & Kriteria Ketercapaian (KKTP)
        - Pemahaman Bermakna & Pertanyaan Pemantik
        
        BAGIAN 3: LANGKAH PEMBELAJARAN ({model_belajar})
        - Pendahuluan
        - Kegiatan Inti (Sintaks {model_belajar} harus terlihat jelas)
        - Penutup
        
        BAGIAN 4: DIFERENSIASI PEMBELAJARAN
        - Strategi untuk Murid Paham Cepat (Pengayaan/Tutor Sebaya)
        - Strategi untuk Murid Butuh Bimbingan (Pendampingan Khusus)
        
        BAGIAN 5: ASESMEN & EVALUASI (SUPER LENGKAP)
        - Kisi-kisi / Blueprint Soal Singkat
        - 3 Soal Pilihan Ganda Kompleks (HOTS)
        - 3 Soal Essay Analisis Kasus ({mode_soal})
        - Kunci Jawaban & Pedoman Penskoran
        - Lembar Observasi Sikap & Rubrik Penilaian
        
        Pastikan bahasa yang digunakan profesional, operasional, dan aplikatif untuk SMK.
        """

        with st.spinner("🤖 Sedang meracik Modul Pro (ATP, Soal HOTS, Rubrik)... Mohon tunggu..."):
            response = model.generate_content(prompt)
            hasil = response.text
            
            st.success("✅ BERHASIL! Modul Super Pro telah jadi.")
            
            # Tampilkan Preview
            with st.expander("📄 Lihat Preview Dokumen", expanded=True):
                st.markdown(hasil)
            
            # Siapkan Word
            doc_file = create_docx(hasil, {
                "sekolah": sekolah, 
                "mapel": mapel, 
                "kelas": kelas, 
                "materi": materi
            })
            
            st.download_button(
                label="📥 DOWNLOAD DOKUMEN WORD (.DOCX)",
                data=doc_file.getvalue(),
                file_name=f"Modul_Pro_{mapel}_{materi}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Terjadi Kendala: {e}")
        st.warning("Tips: Coba refresh halaman atau cek API Key Anda.")