import faiss
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

class FAISSIndex:
    def __init__(self, faiss_index, metadata):
        self.index = faiss_index
        self.metadata = metadata

    def similarity_search(self, query_embedding, k=3):
        # FAISS potrzebuje tablicy numpy o typie float32
        query_vector = np.array([query_embedding]).astype("float32")
        D, I = self.index.search(query_vector, k)
        
        results = []
        for idx in I[0]:
            if idx != -1: # Sprawdzamy, czy znaleziono wynik
                results.append(self.metadata[idx])
        return results

# Nazwa modelu - ten jest darmowy, szybki i popularny
embed_model_id = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {"device": "cpu", "trust_remote_code": True}

def create_index(documents):
    # Załadowanie modelu embeddingowego
    embeddings = HuggingFaceEmbeddings(model_name=embed_model_id, model_kwargs=model_kwargs)
    
    # Wyciągamy sam tekst do wektoryzacji
    texts = [doc['text'] for doc in documents]
    metadata = documents # Zachowujemy całe słowniki jako metadane

    # Zamiana tekstów na wektory
    embeddings_matrix = [embeddings.embed_query(text) for text in texts]
    embeddings_matrix = np.array(embeddings_matrix).astype("float32")

    # Ustawienie indeksu (IndexFlatL2 mierzy odległość euklidesową - im bliżej, tym podobniej)
    dimension = embeddings_matrix.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_matrix)

    return FAISSIndex(index, metadata)

def retrieve_docs(query, faiss_index, k=3):
    # Załadowanie tego samego modelu co przy tworzeniu indeksu
    embeddings = HuggingFaceEmbeddings(model_name=embed_model_id, model_kwargs=model_kwargs)
    
    # Zamiana pytania (query) na wektor
    query_embedding = embeddings.embed_query(query)
    
    # Wywołanie wyszukiwania w obiekcie FAISSIndex
    results = faiss_index.similarity_search(query_embedding, k)
    return results