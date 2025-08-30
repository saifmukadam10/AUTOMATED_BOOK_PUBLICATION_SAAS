from supabase import create_client
import streamlit as st

class SupabaseClient:
    def __init__(self):
        self.url = st.secrets["SUPABASE_URL"]
        self.key = st.secrets["SUPABASE_ANON_KEY"]
        self.client = create_client(self.url, self.key)

    # Insert a new generated document
    def save_document(self, user_id, version, content):
        response = self.client.table("documents").insert({
            "user_id": user_id,
            "version": version,
            "date": "now()",
            "content": content
        }).execute()
        return response

    # Insert reward feedback
    def save_reward(self, user_id, version, score, similarity, readability, errors):
        response = self.client.table("reward_logs").insert({
            "user_id": user_id,
            "version": version,
            "score": score,
            "similarity": similarity,
            "readability": readability,
            "errors": errors,
            "timestamp": "now()"
        }).execute()
        return response

    # Fetch all user documents
    def get_documents(self, user_id):
        response = self.client.table("documents").select("*").eq("user_id", user_id).execute()
        return response.data

    # Fetch all reward logs
    def get_rewards(self, user_id):
        response = self.client.table("reward_logs").select("*").eq("user_id", user_id).execute()
        return response.data
