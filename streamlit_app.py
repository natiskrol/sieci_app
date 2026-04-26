import streamlit as st
from openai import OpenAI
from pdf_reader import extract_text_from_pdf

# 1. Konfiguracja strony
st.set_page_config(layout="wide", page_title="Gemini Chatbot")
st.title("Gemini Chatbot")

# 2. Sidebar - Klucze i pliki
api_key = st.secrets["API_KEY"]
base_url = st.secrets["BASE_URL"]
selected_model = "gemini-2.5-flash"

with st.sidebar:
    uploaded_file = st.file_uploader("Wgraj plik (PDF lub TXT)", type=("pdf", "txt", "md"))
    if st.button("Wyczyść historię"):
        st.session_state.messages = [{"role": "assistant", "content": "W czym mogę Ci pomóc?"}]
        st.rerun()

# 3. Inicjalizacja historii wiadomości
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "W czym mogę Ci pomóc?"}]

# 4. Wyświetlanie historii (WAŻNE: to musi być przed chat_input)
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. Obsługa nowego pytania
if prompt := st.chat_input():
    # Od razu dodajemy i wyświetlamy pytanie użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Przygotowanie treści dla AI (pytanie + ewentualny plik)
    full_prompt = prompt
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            content = extract_text_from_pdf(uploaded_file)
        else:
            content = uploaded_file.read().decode("utf-8")
        
        full_prompt = f"Użytkownik załączył plik o treści:\n{content}\n\nPytanie: {prompt}"

    # Połączenie z API
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # Przygotowanie paczki wiadomości do wysłania (z ukrytym plikiem)
    messages_to_send = st.session_state.messages[:-1] + [{"role": "user", "content": full_prompt}]

    # Pobranie odpowiedzi
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model=selected_model,
            messages=messages_to_send
        )
        msg = response.choices[0].message.content
        st.write(msg)

    # Zapisanie odpowiedzi asystenta do historii
    st.session_state.messages.append({"role": "assistant", "content": msg})