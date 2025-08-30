import csv 
import chromadb
from sentence_transformers import SentenceTransformer, util
import textstat
import language_tool_python
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt

# Initialize ChromaDB Persistent Client
client = chromadb.PersistentClient(path=".chroma_store")
collection = client.get_or_create_collection("chapter_versions")

# Load model and grammar tool
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
tool = language_tool_python.LanguageTool('en-US')

# Reference text for comparison
reference_text = "This is the original reference content of the chapter."

# Reward function (same as before)
def compute_reward(text):
    embedding1 = model.encode(reference_text, convert_to_tensor=True)
    embedding2 = model.encode(text, convert_to_tensor=True)
    similarity_score = util.cos_sim(embedding1, embedding2).item()
    readability_score = textstat.flesch_reading_ease(text)
    grammar_errors = len(tool.check(text))

    final_score = (similarity_score * 0.4) + (readability_score * 0.5) - (grammar_errors * 0.1)
    return final_score, similarity_score, readability_score, grammar_errors

# Function to display leaderboard table
def show_leaderboard():
    results = collection.get(include=["documents", "metadatas"])
    if not results["documents"]:
        print("⚠️ No versions found.")
        return

    leaderboard = []

    for doc, meta in zip(results["documents"], results["metadatas"]):
        final_score, sim, read, errors = compute_reward(doc)
        leaderboard.append([meta["version"], meta["date"], f"{final_score:.2f}", f"{sim:.2f}", f"{read:.2f}", errors])

    # Sort leaderboard by final score (descending)
    leaderboard.sort(key=lambda x: float(x[2]), reverse=True)

    print("\n🏆 📊 Leaderboard of Versions\n")
    print(tabulate(leaderboard, headers=["Version", "Date", "Score", "Similarity", "Readability", "Errors"], tablefmt="pretty"))

# Example toggle inside show_leaderboard()
use_supabase = st.toggle("Use Supabase logs (instead of CSV)", value=False)
if use_supabase:
    try:
        rows = get_rewards_for_user()
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
            if not df.empty:
                plt.figure(figsize=(8,4))
                plt.plot(df["version"], df["score"], marker="o")
                plt.title("Reward Progression (Supabase)")
                plt.xlabel("Version"); plt.ylabel("Score")
                st.pyplot(plt)
        else:
            st.info("No Supabase reward logs yet.")
        
    except Exception as ex:
        st.warning(f"Supabase read failed, falling back to CSV: {ex}")
# (then your existing CSV logic runs)


# Function to plot reward progression from log
import csv
import matplotlib.pyplot as plt

def plot_progression_chart():
    try:
        with open("reward_progression_log.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            versions = []
            scores = []

            for row in reader:
                versions.append(row['version'])
                scores.append(float(row['score']))

        if not versions:
            print("⚠️ No data to plot.")
            return

        plt.figure(figsize=(10, 5))
        plt.plot(versions, scores, marker='o', color='teal')
        plt.title("Reward Score Progression Over Iterations")
        plt.xlabel("Version")
        plt.ylabel("Reward Score")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print("⚠️ reward_progression_log.csv not found.")


if __name__ == "__main__":
    show_leaderboard()
    plot_progression_chart()
