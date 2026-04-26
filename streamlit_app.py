import streamlit as st
from openai import OpenAI
import os
from pdf_reader import extract_text_from_pdf

st.set_page_config(layout="wide", page_title="Gemini chatbot app")
st.title("Gemini chatbot app")
uploaded_file = st.file_uploader("Dodaj plik", type=("txt", "md", "pdf"))

# api_key, base_url = os.environ["API_KEY"], os.environ["BASE_URL"]
api_key, base_url = st.secrets["API_KEY"], st.secrets["BASE_URL"]
selected_model = "gemini-2.5-flash"

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not api_key:
        st.info("Invalid API key.")
        st.stop()

    client = OpenAI(api_key=api_key, base_url=base_url)

    # 1. Przygotowujemy zmienną na pełną treść (pytanie + ewentualny plik)
    full_prompt = prompt 

    # 2. Sprawdzamy, czy użytkownik wgrał jakikolwiek plik
    if uploaded_file is not None:
        # Jeśli to PDF, używamy naszej nowej funkcji z pliku pdf_handler.py
        if uploaded_file.name.endswith('.pdf'):
            from pdf_handler import extract_text_from_pdf
            content = extract_text_from_pdf(uploaded_file)
        else:
            # Jeśli to tekst/markdown, czytamy standardowo
            content = uploaded_file.read().decode("utf-8")
        
        # Łączymy treść pliku z pytaniem
        full_prompt = f"Treść dokumentu:\n{content}\n\nPytanie: {prompt}"

    # 3. Wyświetlamy w chacie TYLKO krótkie pytanie użytkownika (żeby było ładnie)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 4. Do Gemini wysyłamy historię + ten wzbogacony o plik "full_prompt"
    # Podmieniamy ostatnią wiadomość na taką z treścią pliku
    messages_to_send = st.session_state.messages[:-1] + [{"role": "user", "content": full_prompt}]

    response = client.chat.completions.create(
        model=selected_model,
        messages=messages_to_send
    )

    # 5. Wyświetlamy odpowiedź asystenta
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

    client = OpenAI(api_key=api_key, base_url=base_url)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
    model=selected_model,
    messages=st.session_state.messages
)

    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

    
