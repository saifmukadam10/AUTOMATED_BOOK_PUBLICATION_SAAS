import chromadb
from chromadb.config import Settings

# Initialize Persistent Client (same path!)
client = chromadb.PersistentClient(path=".chroma_store")

# Get the collection
collection = client.get_or_create_collection("chapter_versions")

# Define reward function — count unique words
def reward_score(text):
    words = text.split()
    unique_words = set(words)
    return len(unique_words)

# Function to select best version based on reward
def select_best_version():
    results = collection.get(include=["documents", "metadatas"])
    if not results["documents"]:
        print("⚠️ No versions found in database.")
        return

    best_score = -1
    best_version = None
    best_metadata = None

    for doc, meta in zip(results['documents'], results['metadatas']):
        score = reward_score(doc)
        print(f"📊 Version {meta['version']} Score: {score}")

        if score > best_score:
            best_score = score
            best_version = doc
            best_metadata = meta

    print("\n🏆 Best Version Selected:")
    print(f"Version {best_metadata['version']} (Date: {best_metadata['date']})")
    print(f"Reward Score: {best_score}\n")
    print(best_version)

if __name__ == "__main__":
    select_best_version()
