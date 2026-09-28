import time
import streamlit as st
from google import genai

st.set_page_config(page_title="Zafer Asistan", page_icon="🤖")
st.title("🤖 Zafer Asistan Portalınız")

# API Anahtarı kontrolü
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Cloud Secrets ayarlarınızı kontrol edin.")
    st.stop()

# Şifre Kontrolü
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

# Google GenAI İstemcisi
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
            response_text = None
            last_error = None
            
            # Yoğunluk anında sırayla denenecek modeller ve tekrar mekanizması
            candidate_models = ["gemini-3.8-flash", "gemini-3.8-pro", "gemini-1.5-flash"]

            for model_name in candidate_models:
                # Her model için yoğunluk durumunda 2 kez deneme yapılır
                for attempt in range(2):
                    try:
                        res = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        response_text = res.text
                        break
                    except Exception as e:
                        last_error = e
                        if "503" in str(e) or "UNAVAILABLE" in str(e):
                            time.sleep(2)  # Yoğunluk varsa 2 saniye bekle ve tekrar dene
                            continue
                        break
                if response_text:
                    break

            if response_text:
                st.write(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error(f"Sunucu yoğunluğu nedeniyle yanıt alınamadı, lütfen birkaç saniye sonra tekrar deneyin. (Hata: {last_error})")
