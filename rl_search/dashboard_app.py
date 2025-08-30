import streamlit as st
import chromadb
from chromadb.config import Settings
from datetime import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt
import subprocess
import requests
import sys
from difflib import unified_diff

# 🔑 Custom imports
from smart_reward_function import compute_reward
from nlp_utils import correct_grammar_and_style, extract_keywords, check_plagiarism
from auth import require_auth_ui, signout as sb_signout
from database import save_document, log_reward
from supabase_client import SupabaseClient
from feedback_engine import run_feedback_ui   # ✅ Uses your added UI

# ---------------- App Config (place before any UI output) ----------------
st.set_page_config(page_title="📊 Project Dashboard", layout="wide")

# ---------------- Session / Clients ----------------
if "supabase" not in st.session_state:
    st.session_state.supabase = SupabaseClient()
if "user" not in st.session_state:
    st.session_state["user"] = {"id": None, "email": None}

# UI state helpers (safe keys)
for k, v in {
    "draft_text": "",
    "ref_text": "",
    "improved_text": "",
    "rephrased_text": "",
}.items():
    st.session_state.setdefault(k, v)

supabase = st.session_state.supabase

# ---------------- Authentication ----------------
user = require_auth_ui()
if user:
    st.session_state["user"] = {"id": user.id, "email": user.email}
    st.sidebar.markdown(f"**Signed in as:** {user.email}")
else:
    st.stop()

if st.sidebar.button("Sign out"):
    sb_signout()
    st.session_state["user"] = {"id": None, "email": None}
    st.rerun()

user_id = st.session_state["user"]["id"]

# ---------------- Chroma setup ----------------
# If you ever move this to another machine, just keep the same folder name.
client = chromadb.PersistentClient(path=".chroma_store")
collection_name = "chapter_versions"
collection = client.get_or_create_collection(collection_name)

# ---------------- Helpers ----------------
def get_collection_stats():
    try:
        return collection.get(include=["documents", "metadatas"])
    except Exception:
        return None

def reset_collection():
    try:
        client.delete_collection(collection_name)
        st.success(f"✅ Collection '{collection_name}' reset.")
    except Exception as e:
        st.error(f"❌ Error deleting collection: {e}")

def show_leaderboard():
    log_file = "reward_progression_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)

        st.subheader("📊 Reward Progression Log")
        st.dataframe(df)

        if not df.empty and "Version" in df.columns and "Final Score" in df.columns:
            plt.figure(figsize=(8, 4))
            plt.plot(df["Version"], df["Final Score"], marker="o")
            plt.title("Reward Progression Over Versions")
            plt.xlabel("Version")
            plt.ylabel("Final Score")
            st.pyplot(plt)
            plt.close()
    else:
        st.warning("⚠️ No reward_progression_log.csv found.")

def preload_sample_document():
    try:
        collection.add(
            documents=["This is a test document for debugging."],
            metadatas=[{"version": "0", "date": "2025-07-02 16:00:00"}],
            ids=["version_0"],
        )
        st.success("✅ Sample document added to collection.")
    except Exception as e:
        st.error(f"❌ Error adding sample document: {e}")

def show_version_summary():
    results = get_collection_stats()
    if results and results.get("documents"):
        st.subheader("📖 Version Summary")
        for doc, meta in zip(results["documents"], results["metadatas"]):
            st.markdown(
                f"**Version {meta.get('version','?')} (Date: {meta.get('date','?')})**"
            )
            st.code(doc)
    else:
        st.info("ℹ️ No documents found in collection.")

def show_version_differences():
    results = get_collection_stats()
    if results and results.get("documents") and len(results["documents"]) >= 2:
        st.subheader("🔍 Compare Document Versions")
        version_options = [
            f"Version {meta.get('version','?')}" for meta in results["metadatas"]
        ]
        idx1 = st.selectbox(
            "Select first version:",
            list(range(len(version_options))),
            format_func=lambda i: version_options[i],
        )
        idx2 = st.selectbox(
            "Select second version:",
            list(range(len(version_options))),
            format_func=lambda i: version_options[i],
            index=1 if len(version_options) > 1 else 0,
        )

        doc1 = results["documents"][idx1]
        doc2 = results["documents"][idx2]

        diff = unified_diff(
            doc1.splitlines(),
            doc2.splitlines(),
            lineterm="",
            fromfile="Version A",
            tofile="Version B",
        )

        st.write("### 🧾 Diff")
        st.code("\n".join(diff))
    else:
        st.warning("⚠️ Need at least two documents to compare.")

def rephrase_with_ollama(prompt_text, model_name="llama3"):
    """Uses local Ollama (http://localhost:11434)."""
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model_name,
            "prompt": f"Rephrase this text improving grammar, clarity, and readability:\n\n{prompt_text}\n\nRephrased:",
            "stream": False,
        }
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"⚠️ Ollama error: {e}"

# ---------------- Reward Normalization ----------------
def _coerce_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def _coerce_int(x, default=0):
    try:
        return int(float(x))
    except Exception:
        return default

def safe_compute_reward(text: str, reference_text: str = None):
    """
    Adaptor layer that accepts whatever compute_reward returns:
    - dict with keys: score, similarity, readability, errors
    - tuple/list: (score, similarity, readability, errors)
    """
    if not text or not isinstance(text, str) or not text.strip():
        st.error("❌ Draft text is empty.")
        return None

    try:
        res = compute_reward(text, reference_text)
    except Exception as e:
        st.error(f"⚠️ compute_reward crashed: {e}")
        return None

    score = sim = read = 0.0
    errors = 0

    if isinstance(res, dict):
        score = _coerce_float(res.get("score", 0.0))
        sim = _coerce_float(res.get("similarity", 0.0))
        read = _coerce_float(res.get("readability", 0.0))
        errors = _coerce_int(res.get("errors", 0))
    elif isinstance(res, (list, tuple)) and len(res) >= 4:
        score = _coerce_float(res[0])
        sim = _coerce_float(res[1])
        read = _coerce_float(res[2])
        errors = _coerce_int(res[3])
    else:
        st.error("⚠️ Unexpected shape from compute_reward. Expected dict or 4-tuple.")
        return None

    return score, sim, read, errors

# ---------------- Draft Editor (fixed) ----------------
def draft_editor():
    st.subheader("📝 Draft Editor")

    # 🔹 Initialize canonical states if not already present
    if "draft_text" not in st.session_state:
        st.session_state["draft_text"] = ""
    if "ref_text" not in st.session_state:
        st.session_state["ref_text"] = ""

    col1, col2 = st.columns([2, 1])
    with col1:
        # Main draft area: bind to widget key, but use canonical draft_text for value
        draft_text = st.text_area(
            "Write your draft:",
            value=st.session_state["draft_text"],
            key="draft_text_widget",
            height=300,
        )
        st.session_state["draft_text"] = draft_text  # keep canonical copy

        ref_text = st.text_area(
            "Reference Text (optional):",
            value=st.session_state["ref_text"],
            key="ref_text_widget",
            height=150,
        )
        st.session_state["ref_text"] = ref_text

    with col2:
        st.markdown("**Tools**")

        # 1) Improve Grammar & Style
        if st.button("✨ Improve Grammar & Style"):
            draft = st.session_state["draft_text"].strip()
            if draft:
                try:
                    st.session_state["improved_text"] = correct_grammar_and_style(draft)
                    st.success("✅ Draft improved. Review the preview below, then click 'Apply Improved Text'.")
                except Exception as e:
                    st.error(f"⚠️ Grammar/Style failed: {e}")
            else:
                st.error("Please enter draft text first.")

        # 2) Keywords
        if st.button("🔑 Extract Keywords"):
            draft = st.session_state["draft_text"].strip()
            if draft:
                try:
                    kws = extract_keywords(draft)
                    st.write(kws)
                except Exception as e:
                    st.error(f"⚠️ Keyword extraction failed: {e}")
            else:
                st.error("Please enter draft text first.")

        # 3) Plagiarism
        if st.button("🧪 Check Plagiarism"):
            draft = st.session_state["draft_text"].strip()
            if draft:
                try:
                    report = check_plagiarism(draft)
                    st.write(report)
                except Exception as e:
                    st.error(f"⚠️ Plagiarism check failed: {e}")
            else:
                st.error("Please enter draft text first.")

    # If there's an improved version, show it with an Apply button
    if st.session_state.get("improved_text"):
        st.markdown("#### ✍️ Improved Preview")
        st.text_area(
            "Improved Draft (preview)",
            value=st.session_state["improved_text"],
            key="improved_preview",
            height=180,
        )
        if st.button("✅ Apply Improved Text"):
            # ✅ Update canonical draft only
            st.session_state["draft_text"] = st.session_state["improved_text"]
            st.session_state["improved_text"] = ""  # clear preview
            st.success("✅ Applied improved text.")
            st.rerun()

    st.divider()
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("📈 Evaluate Draft"):
            draft = st.session_state["draft_text"]
            res = safe_compute_reward(draft, st.session_state["ref_text"])
            if res:
                score, sim, read, errors = res
                st.success("✅ Evaluation complete.")
                st.write(
                    f"**Reward Score:** {score:.2f} | Similarity {sim:.2f} | "
                    f"Readability {read:.2f} | Errors {errors}"
                )

    with c2:
        if st.button("💾 Save as Candidate"):
            draft = st.session_state["draft_text"].strip()
            if draft:
                with open("latest_candidate.txt", "w", encoding="utf-8") as f:
                    f.write(draft)
                st.success("✅ Saved to latest_candidate.txt")
            else:
                st.error("Please enter draft text first.")

    with c3:
        if st.button("☁️ Save as New Version"):
            draft = st.session_state["draft_text"].strip()
            if draft:
                try:
                    results = collection.get(include=["metadatas"])
                    existing_versions = [
                        int(m["version"]) for m in (results["metadatas"] or [])
                    ] if results else []
                    new_version_number = (
                        max(existing_versions) + 1 if existing_versions else 1
                    )
                except Exception:
                    new_version_number = 1

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    collection.add(
                        documents=[draft],
                        metadatas=[{"version": str(new_version_number), "date": timestamp}],
                        ids=[f"version_{new_version_number}"],
                    )
                    save_document(new_version_number, draft, timestamp)
                    st.success(f"✅ Version {new_version_number} saved to Chroma & Supabase.")
                except Exception as e:
                    st.error(f"❌ Save failed: {e}")
            else:
                st.error("Please enter draft text first.")

# ---------------- AI Rewrite Review (fixed) ----------------
def ai_rewrite_review():
    candidate_file = "latest_candidate.txt"
    st.subheader("📄 Candidate Version Content")

    if os.path.exists(candidate_file):
        with open(candidate_file, "r", encoding="utf-8") as f:
            candidate_text = f.read()

        # Handle staged rephrased text safely
        if "candidate_editor_temp" in st.session_state:
            editor_value = st.session_state["candidate_editor_temp"]
            del st.session_state["candidate_editor_temp"]
        else:
            editor_value = st.session_state.get("candidate_editor", candidate_text)

        # Editable text box
        edited_text = st.text_area(
            "Editable Text",
            value=editor_value,
            key="candidate_editor",
            height=400
        )

        # Rephrase via Ollama ⇒ goes to preview box (no in-place overwrite)
        if st.button("🤖 Rephrase with Ollama"):
            st.session_state["rephrased_text"] = rephrase_with_ollama(edited_text)

        # Show rephrased output if available
        if st.session_state.get("rephrased_text", ""):
            st.text_area(
                "Rephrased Output",
                st.session_state["rephrased_text"],
                key="rephrased_output",
                height=300
            )
            if st.button("⬅️ Use Rephrased As Edited"):
                # Stage the new content in a temp key, then rerun
                st.session_state["candidate_editor_temp"] = st.session_state["rephrased_text"]
                st.session_state["rephrased_text"] = ""
                st.rerun()

        # Evaluate current edited text
        res = safe_compute_reward(edited_text)
        if not res:
            return
        final_score, sim, read, errors = res
        st.write(
            f"**Reward Score:** {final_score:.2f} | Similarity {sim:.2f} | "
            f"Readability {read:.2f} | Errors {errors}"
        )

        if st.button("✅ Approve & Save"):
            try:
                results = collection.get(include=["metadatas"])
                existing_versions = [
                    int(meta["version"]) for meta in results["metadatas"]
                ] if results and results.get("metadatas") else []
                new_version_number = (
                    max(existing_versions) + 1 if existing_versions else 1
                )
            except Exception:
                new_version_number = 1

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                collection.add(
                    documents=[edited_text],
                    metadatas=[
                        {"version": str(new_version_number), "date": timestamp}
                    ],
                    ids=[f"version_{new_version_number}"],
                )
            except Exception as e:
                st.error(f"❌ Could not add to Chroma: {e}")

            # Log to Supabase & CSV
            try:
                save_document(new_version_number, edited_text, timestamp)
                log_reward(new_version_number, final_score, sim, read, errors, timestamp)
                st.info("☁️ Synced to Supabase.")
            except Exception as ex:
                st.warning(f"Could not sync to Supabase: {ex}")

            # Append to local CSV for leaderboard
            try:
                row = {
                    "Version": new_version_number,
                    "Final Score": final_score,
                    "Similarity": sim,
                    "Readability": read,
                    "Errors": errors,
                    "Timestamp": timestamp,
                }
                if os.path.exists("reward_progression_log.csv"):
                    df = pd.read_csv("reward_progression_log.csv")
                    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                else:
                    df = pd.DataFrame([row])
                df.to_csv("reward_progression_log.csv", index=False)
            except Exception as e:
                st.warning(f"Could not update local leaderboard CSV: {e}")

            st.success("✅ Approved and saved.")
            try:
                os.remove(candidate_file)
            except Exception:
                pass
    else:
        st.info("ℹ️ No candidate version found. Save one from **Draft Editor**.")

# ---------------- Rephrasing Loop ----------------
def run_rephrasing_loop():
    try:
        result = subprocess.run(
            [sys.executable, "rl_search/rephrasing_loop.py"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

# ---------------- Sidebar Navigation ----------------
st.title("📖 Automated Book Publication — Admin Dashboard")

option = st.sidebar.radio(
    "Go to",
    (
        "📝 Draft Editor",
        "📊 Leaderboard Viewer",
        "📑 Version Summary",
        "🔍 Compare Versions",
        "📄 AI Rewrite Review",
        "🧹 Chroma Maintenance",
        "📖 Run AI Rephrasing Loop",
        "📬 Feedback",
    ),
)

# ---------------- Router ----------------
if option == "📝 Draft Editor":
    draft_editor()
elif option == "📊 Leaderboard Viewer":
    show_leaderboard()
elif option == "📑 Version Summary":
    show_version_summary()
elif option == "🔍 Compare Versions":
    show_version_differences()
elif option == "📄 AI Rewrite Review":
    ai_rewrite_review()
elif option == "🧹 Chroma Maintenance":
    stats = get_collection_stats()
    if stats and stats.get("documents"):
        st.success(f"✅ Collection has {len(stats['documents'])} docs.")
        if st.button("⚠️ Reset Collection"):
            reset_collection()
    else:
        if st.button("➕ Preload Sample Document"):
            preload_sample_document()
elif option == "📖 Run AI Rephrasing Loop":
    if st.button("▶️ Start Rephrasing Now"):
        success, msg = run_rephrasing_loop()
        st.write(msg)
elif option == "📬 Feedback":
    run_feedback_ui()  # ✅ Hooked in feedback_engine
