import chromadb

client = chromadb.Client()
collection = client.create_collection("my_notes")

# Add some documents
collection.add(
    documents=[
        "TCP uses a three-way handshake: SYN, SYN-ACK, ACK",
        "UDP is connectionless and does not guarantee delivery",
        "DNS translates domain names to IP addresses",
        "MQTT is a lightweight messaging protocol for IoT devices",
        "LoRa is a long-range, low-power wireless protocol used by Meshtastic",
    ],
    ids=["tcp", "udp", "dns", "mqtt", "lora"],
)

# Query — find documents similar to this question
query = "how do devices communicate wirelessly?"
results = collection.query(query_texts=[query], n_results=2)

print(f"Query: {query}\n")
print("Most relevant documents:")
for doc in results["documents"][0]:
    print(f"  → {doc}")
