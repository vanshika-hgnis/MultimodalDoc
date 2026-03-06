import os
import ollama

client = ollama.Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)

# This will list the available models
response = client.get("/api/tags")
print(response.json())