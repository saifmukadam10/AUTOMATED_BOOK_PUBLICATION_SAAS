import os
from datetime import datetime
from supabase import create_client
from smart_reward_function import compute_reward
import streamlit as st

# ------------------------------
# Supabase Connection (Service Role Key)
# ------------------------------
SUPABASE_URL = "https://isrzxefziojidmacpihl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlzcnp4ZWZ6aW9qaWRtYWNwaWhsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTM2MjU5OSwiZXhwIjoyMDcwOTM4NTk5fQ._BBS1rwczbn_QjRHjsB5RjUeQKkXfju1u2npvJzpXA0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------------------
# Feedback Engine Core
# ------------------------------
def evaluate_and_log(user_id: str, version: int, text: str, reference_text: str = None):
    """
    Evaluate a draft using the reward function and log results to Supabase.
    """
    # 1. Compute reward
    reward_results = compute_reward(text, reference_text)

    # 2. Insert into Supabase logs
    log_entry = {
        "user_id": user_id,
        "version": version,
        "similarity": reward_results.get("similarity", 0.0),
        "readability": reward_results.get("readability", 0.0),
        "errors": reward_results.get("errors", 0),
        "score": reward_results.get("score", 0.0),
        "timestamp": datetime.utcnow().isoformat()
    }

    supabase.table("reward_logs").insert(log_entry).execute()
    print(f"✅ Logged reward results for user {user_id}, version {version}")

    return reward_results


# ------------------------------
# Feedback Engine UI (for dashboard_app)
# ------------------------------
def run_feedback_ui():
    """
    Streamlit UI to test feedback engine inside dashboard_app.py
    """
    st.header("📊 Feedback Engine")

    user_id = st.text_input("User ID (UUID)", value="11111111-2222-3333-4444-555555555555")
    version = st.number_input("Version", min_value=1, value=1, step=1)
    text = st.text_area("Draft Text", "This is an example draft written by a user. It should be clear and readable.")
    reference_text = st.text_area("Reference Text (optional)", "This is the original reference content of the chapter.")

    if st.button("Evaluate & Log"):
        if text.strip():
            results = evaluate_and_log(user_id, version, text, reference_text)
            st.success("✅ Evaluation complete and logged to Supabase!")
            st.json(results)
        else:
            st.error("❌ Please enter some draft text.")


# ------------------------------
# Manual Test (Run directly)
# ------------------------------
if __name__ == "__main__":
    sample_text = "This is an example draft written by a user. It should be clear and readable."
    reference_text = "This is the original reference content of the chapter."
    fake_user_id = "11111111-2222-3333-4444-555555555555"
    version = 1

    results = evaluate_and_log(fake_user_id, version, sample_text, reference_text)
    print("📊 Evaluation Results:", results)
