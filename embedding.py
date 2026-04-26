def get_embedding(text, client, model="text-embedding-3-small"):
    # Usuwamy znaki nowej linii dla lepszej jakości
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding