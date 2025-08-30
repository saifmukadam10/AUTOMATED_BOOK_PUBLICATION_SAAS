import streamlit as st
import chromadb
from chromadb.config import Settings
import pandas as pd
import os
import matplotlib.pyplot as plt

# Initialize Chroma client
client = chromadb.PersistentClient(path=".chroma_store")
collection_name = "chapter_versions"

# Function to fetch collection stats
def get_collection_stats():
    try:
        collection = client.get_collection(collection_name)
        results = collection.get(include=["documents", "metadatas"])
        return results
    except Exception as e:
        return None

# Function to reset collection
def reset_collection():
    try:
        client.delete_collection(collection_name)
        st.success(f"✅ Collection '{collection_name}' has been reset.")
    except Exception as e:
        st.error(f"❌ Error deleting collection: {e}")

# Function to display leaderboard from CSV log
def show_leaderboard():
    if os.path.exists("reward_progression_log.csv"):
        df = pd.read_csv("reward_progression_log.csv", names=["Timestamp", "Version", "Score", "Similarity", "Readability", "Errors"])
        st.subheader("📊 Reward Progression Log")
        st.dataframe(df)

        # Plot chart only if there’s data
        if not df.empty:
            plt.figure(figsize=(8, 4))
            plt.plot(df["Version"], df["Score"], marker="o")
            plt.title("Reward Progression Over Versions")
            plt.xlabel("Version")
            plt.ylabel("Score")
            st.pyplot(plt)
        else:
            st.info("ℹ️ No reward progression data available to plot.")
    else:
        st.warning("⚠️ reward_progression_log.csv not found.")

# Function to preload a test document into Chroma
def preload_sample_document():
    try:
        collection = client.get_or_create_collection(collection_name)
        collection.add(
            documents=["This is a test document for debugging."],
            metadatas=[{"version": "0", "date": "2025-07-02 16:00:00"}],
            ids=["version_0"]
        )
        st.success("✅ Sample document added to collection.")
    except Exception as e:
        st.error(f"❌ Error adding sample document: {e}")

# Streamlit Page Layout
st.set_page_config(page_title="📊 Project Maintenance Dashboard", layout="wide")

st.title("📖 Automated Book Publication — Admin Dashboard")

# Sidebar Navigation
option = st.sidebar.radio("Go to", ("📊 Leaderboard Viewer", "🧹 Chroma Collection Maintenance"))

# Main content based on selection
if option == "📊 Leaderboard Viewer":
    st.header("📊 Leaderboard & Reward Progression")
    show_leaderboard()

elif option == "🧹 Chroma Collection Maintenance":
    st.header("🧹 Manage Chroma Collections")
    stats = get_collection_stats()

    if stats and stats['documents']:
        st.success(f"✅ Collection '{collection_name}' contains {len(stats['documents'])} documents.")
        st.write("📄 Example Document:", stats['documents'][0])

        if st.button("⚠️ Reset Collection"):
            reset_collection()
    else:
        st.warning(f"⚠️ Collection '{collection_name}' is empty or missing.")
        if st.button("➕ Preload Sample Document"):
            preload_sample_document()
