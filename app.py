import os
import sqlite3
import streamlit as st
import google.generativeai as genai

# --- 1. GÜVENLİK VE GİRİŞ KONTROLÜ ---
st.set_page_config(page_title="Zafer Asistan", page_icon="🧠", layout="centered")

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Özel Asistan Girişi")
        pwd = st.text_input("Sistem Giriş Şifresi:", type="password")
        if st.button("Giriş Yap"):
            if pwd == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
        return False
    return True

if not check_password():
    st.stop()

# --- 2. KALICI HAFIZA (SQLITE VERİTABANI) ---
conn = sqlite3.connect("hafiza.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS sohbetler 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, rol TEXT, mesaj TEXT)''')
conn.commit()

# --- 3. API & MODEL AYARLARI ---
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.warning("⚠️ Lütfen Streamlit Secrets alanına GEMINI_API_KEY ekleyin.")
    st.stop()

genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
Sen kullanıcının kişisel, bağımsız ve sınırsız özel asistanısın.
Sürekli olarak kullanıcının geçmiş sohbetlerini, tercihlerini, teknik uzmanlığını ve üslubunu hatırla.
Kullanıcıya her zaman doğrudan, teknik düzeyi yüksek, samimi ve iş odaklı yanıtlar ver.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# --- 4. ARAYÜZ VE SOHBET MANTIĞI ---
st.title("🤖 Zafer Asistan Portalınız")

c.execute("SELECT rol, mesaj FROM sohbetler ORDER BY id ASC")
gecmis = c.fetchall()

messages = []
for rol, mesaj in gecmis:
    messages.append({"role": rol, "parts": [mesaj]})
    with st.chat_message(rol):
        st.write(mesaj)

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.chat_message("user").write(prompt)
    c.execute("INSERT INTO sohbetler (rol, mesaj) VALUES (?, ?)", ("user", prompt))
    conn.commit()
    
    chat = model.start_chat(history=messages)
    response = chat.send_message(prompt)
    
    st.chat_message("assistant").write(response.text)
    c.execute("INSERT INTO sohbetler (rol, mesaj) VALUES (?, ?)", ("assistant", response.text))
    conn.commit()
