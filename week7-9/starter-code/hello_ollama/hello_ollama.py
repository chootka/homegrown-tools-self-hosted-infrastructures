import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "tinyllama",
    "prompt": "What is a mesh network?",
    "stream": False,
})

print(response.json()["response"])
