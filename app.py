import streamlit as st
from google import genai

st.set_page_config(page_title="Zafer Asistan", page_icon="🤖")
st.title("🤖 Zafer Asistan Portalınız")

# API Anahtarı kontrolü
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Cloud Secrets ayarlarınızı kontrol edin.")
    st.stop()

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

# Client Tanımlama
client = genai.Client(api_key=api_key)

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
            # Güncel ve geçerli modeller sırasıyla denenir
            candidate_models = [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash"
            ]
            
            response_text = None
            last_error = None

            for model_name in candidate_models:
                try:
                    res = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    response_text = res.text
                    break
                except Exception as e:
                    last_error = e
                    continue

            if response_text:
                st.write(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error(f"Sistemdeki tüm modeller denendi ancak yanıt alınamadı. Son hata: {last_error}")
