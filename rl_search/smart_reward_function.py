import os


import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, util
import textstat
import language_tool_python
import numpy as np
from huggingface_hub import snapshot_download

# ✅ Now safely download model snapshot
snapshot_download(repo_id="sentence-transformers/all-MiniLM-L6-v2", local_dir_use_symlinks=False)

# ✅ Now load your model cleanly
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', use_auth_token=None)


# Initialize Persistent Client (same path!)
client = chromadb.PersistentClient(path=".chroma_store")

# Get the collection
collection = client.get_or_create_collection("chapter_versions")

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
tool= language_tool_python.LanguageTool('en-US')
reference_text = "This is the original reference content of the chapter."


# Define reward function
def compute_reward(text):
    #text Similarity
    embedding1=model.encode(reference_text,convert_to_tensor=True)
    embedding2=model.encode(text,convert_to_tensor=True)
    similarity_score=util.cos_sim(embedding1,embedding2).item()

    #readabilty score
    readability_score=textstat.flesch_reading_ease(text)
    #Formula-206.835−1.015×(words per sentence)−84.6×(syllables per word)
    
    #Grammer Check
    grammar_matches=tool.check(text)
    grammar_errors=len(grammar_matches)

    # combine Scores
    final_score = (similarity_score * 0.4) + (readability_score * 0.5) - (grammar_errors * 0.1)
    return final_score, similarity_score, readability_score, grammar_errors


# Function to select best version based on reward
def select_best_version():
    results = collection.get(include=["documents", "metadatas"])
    if not results["documents"]:
        print("⚠️ No versions found in database.")
        return

    best_score = -np.inf #ensures any valid score will be higher
    best_version = None
    best_metadata = None

    for doc, meta in zip(results['documents'], results['metadatas']):
        final_score, sim, read, errors = compute_reward(doc)
        print(f"📊 Version {meta['version']} — Score: {final_score:.2f}, Similarity: {sim:.2f}, Readability: {read:.2f}, Errors: {errors}")


        if final_score > best_score:
            best_score = final_score
            best_version = doc
            best_metadata = meta


    print("\n🏆 Best Version Selected:")
    print(f"Version {best_metadata['version']} (Date: {best_metadata['date']})")
    print(f"Final Score: {best_score:.2f}\n")
    print(best_version)

if __name__ == "__main__":
    select_best_version()
