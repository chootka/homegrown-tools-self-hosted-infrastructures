import requests

print("Chat with your local LLM. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "tinyllama",
        "prompt": user_input,
        "stream": False,
    })

    print(f"LLM: {response.json()['response']}\n")
