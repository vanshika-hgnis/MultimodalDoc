import os
from ollama import Client

api_key = os.getenv("OLLAMA_API_KEY")

if api_key is None:
    raise ValueError("OLLAMA_API_KEY environment variable is not set!")

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": "Bearer " + api_key
    }
)

# Example: Requesting available models (replace with actual API interaction as per your use case)
models = client.chat("gpt-oss:120b", [{"role": "user", "content": "What models are available?"}])

print(models)