import streamlit as st
import chromadb
from chromadb.config import Settings
from datetime import datetime
import os
import matplotlib.pyplot as plt
from smart_reward_function import compute_reward

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=".chroma_store")
collection = client.get_or_create_collection("chapter_versions")

# Load candidate text file (from rephrasing loop)
candidate_file = "latest_candidate.txt"

# Page config
st.set_page_config(page_title="📝 Human-in-the-Loop Review", layout="wide")
st.title("📝 Human Review & Approval with Live Metrics")

if os.path.exists(candidate_file):
    with open(candidate_file, "r", encoding="utf-8") as f:
        candidate_text = f.read()

    st.subheader("📄 Candidate Version Content")

    # Editable Text Area with session state
    if 'edited_text' not in st.session_state:
        st.session_state.edited_text = candidate_text

    edited_text = st.text_area("✏️ Edit the text before approval (if needed):", 
                               value=st.session_state.edited_text, 
                               height=400, key="editable_text_area")

    st.session_state.edited_text = edited_text  # update session state

    # Compute live reward metrics
    final_score, sim, read, errors = compute_reward(edited_text)

    st.subheader("📊 Live Metrics")
    st.write(f"**Similarity Score:** {sim:.2f}")
    st.write(f"**Readability Score:** {read:.2f}")
    st.write(f"**Grammar Errors:** {errors}")
    st.write(f"**Final Reward Score:** {final_score:.2f}")

    # Approve or Discard Buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approve and Save to Chroma"):
            results = collection.get(include=["metadatas"])
            existing_versions = [int(meta['version']) for meta in results['metadatas']] if results['metadatas'] else [0]
            new_version_number = max(existing_versions) + 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Add approved text to ChromaDB
            collection.add(
                documents=[edited_text],
                metadatas=[{"version": str(new_version_number), "date": timestamp}],
                ids=[f"version_{new_version_number}"]
            )

            # Log to CSV
            log_entry = f"{timestamp},{new_version_number},{final_score:.2f},{sim:.2f},{read:.2f},{errors}\n"
            with open("reward_progression_log.csv", "a") as log_file:
                log_file.write(log_entry)

            st.success("✅ Approved and saved successfully!")

            # Delete candidate file
            os.remove(candidate_file)

            # Reset session state to avoid leftover text
            st.session_state.edited_text = ""

    with col2:
        if st.button("❌ Discard Candidate"):
            os.remove(candidate_file)
            st.warning("⚠️ Candidate discarded.")
            st.session_state.edited_text = ""

else:
    st.info("ℹ️ No candidate version found. Run the rephrasing loop first.")


