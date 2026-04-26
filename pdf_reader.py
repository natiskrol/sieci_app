import fitz  # PyMuPDF

def extract_text_from_pdf(uploaded_file):
    text = ""
    # Otwieramy dokument z pamięci (Streamlit przechowuje go jako BytesIO)
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text
    