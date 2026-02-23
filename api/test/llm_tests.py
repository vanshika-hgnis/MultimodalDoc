import requests
r = requests.post(
    "http://localhost:11434/api/embeddings",
    json={"model":"nomic-embed-text","prompt":"hello"}
)
emb = r.json()["embedding"]
print("dim =", len(emb))
PY