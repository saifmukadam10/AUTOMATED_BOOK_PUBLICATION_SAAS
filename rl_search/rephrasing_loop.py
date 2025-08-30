import requests
import json
from datetime import datetime
import chromadb
from chromadb.config import Settings
from smart_reward_function import compute_reward

client = chromadb.PersistentClient(path=".chroma_store")
collection = client.get_or_create_collection("chapter_versions")

def rephrase_with_ollama(prompt_text, model_name="llama3"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": f"Rephrase the following text to improve grammar, readability and keep meaning intact:\n\n{prompt_text}\n\nRephrased Version:",
        "stream": False
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "").strip()   # ✅ safer

def safe_float(value, fallback=0.0):
    try:
        return float(value)
    except Exception:
        print(f"Warning: Could not convert '{value}' to float. Using {fallback}.")
        return fallback

def iterative_rephrasing_and_logging(iterations=5):
    # Debug check
    print("DEBUG compute_reward output:", compute_reward("test text"))

    results = collection.get(include=["documents", "metadatas"])

    if not results["documents"]:
        print("No versions found. Seeding initial version...")
        initial_text = """This is the initial draft text. Replace it with your actual text."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        collection.add(
            documents=[initial_text],
            metadatas=[{"version": "0", "date": timestamp}],
            ids=["version_0"]
        )

        results = collection.get(include=["documents", "metadatas"])

    # Now safe to proceed
    current_best = results['documents'][0]
    current_meta = results['metadatas'][0]

    # compute_reward returns dict
    best_metrics = compute_reward(current_best)
    best_score = safe_float(best_metrics.get("score", 0.0))

    # Default version handling
    current_version_number = int(current_meta.get("version", 0))

    best_metrics = compute_reward(current_best)
    best_score = safe_float(best_metrics.get("score", 0.0))

    for i in range(iterations):
        print(f"\n Iteration {i+1}")

        # Rephrase via Ollama
        new_version = rephrase_with_ollama(current_best)

        # Compute new reward
        result = compute_reward(new_version)
        new_score = safe_float(result.get("score", 0.0))
        sim = safe_float(result.get("similarity", 0.0))
        read = safe_float(result.get("readability", 0.0))
        errors = result.get("errors", 0)

        print(
            f"New Score: {new_score:.2f} | "
            f"Similarity: {sim:.2f} | "
            f"Readability: {read:.2f} | "
            f"Errors: {errors}"
        )

        # If improved, save in Chroma
        if new_score > best_score:
            print("New version accepted.")
            current_best = new_version
            best_score = new_score
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_version_number = current_version_number + 1
            current_version_number = new_version_number   # ✅ update tracker

            collection.add(
                documents=[new_version],
                metadatas=[{"version": str(new_version_number), "date": timestamp}],
                ids=[f"version_{new_version_number}"]
            )

            with open("reward_progression.log", "a") as log_file:
                log_file.write(f"{timestamp} | Version {new_version_number} | Score: {new_score:.2f}\n")

        else:
            print("New version discarded. No improvement.")

    print("\n Iterative rephrasing complete.")

if __name__ == "__main__":
    iterative_rephrasing_and_logging(iterations=5)
