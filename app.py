import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Zafer Asistan", page_icon="🤖")

st.title("🤖 Zafer Asistan Portalınız")

# API Anahtarı kontrolü
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Cloud Secrets ayarlarınızı kontrol edin.")
    st.stop()

# API Yapılandırması
genai.configure(api_key=api_key)

# Giriş/Şifre Kontrolü
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Sistem Giriş Şifresi", type="password")
    if st.button("Giriş Yap"):
        if pwd == "1234":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Hatalı şifre!")
    st.stop()

# Model Tanımlama
SYSTEM_PROMPT = "Sen Zafer Asistan adında yardımsever, kişisel bir yapay zeka asistanısın."

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Sohbet Geçmişi Hazırlığı
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş Mesajları Listele
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Kullanıcı Mesaj Girişi
prompt = st.chat_input("Mesajınızı yazın...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            try:
                history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
                
