# database.py
from typing import Optional, List, Dict, Any
from datetime import datetime
import streamlit as st
from auth import get_supabase, current_user

# Tables expected in Supabase (Postgres):
# documents(id uuid default gen_random_uuid() pk, user_id text, version int, date timestamptz, content text)
# reward_logs(id uuid default gen_random_uuid() pk, user_id text, version int, score float, similarity float, readability float, errors int, timestamp timestamptz)

def save_document(version: int, content: str, date_str: Optional[str] = None):
    user = current_user()
    if not user:
        raise RuntimeError("Not authenticated")

    sb = get_supabase()
    timestamp = date_str or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "user_id": user.id,
        "version": int(version),
        "date": timestamp,
        "content": content,
    }
    return sb.table("documents").insert(data).execute()

def log_reward(version: int, score: float, similarity: float, readability: float, errors: int, ts: Optional[str] = None):
    user = current_user()
    if not user:
        raise RuntimeError("Not authenticated")

    sb = get_supabase()
    timestamp = ts or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "user_id": user.id,
        "version": int(version),
        "score": float(score),
        "similarity": float(similarity),
        "readability": float(readability),
        "errors": int(errors),
        "timestamp": timestamp,
    }
    return sb.table("reward_logs").insert(data).execute()

def get_documents_for_user() -> List[Dict[str, Any]]:
    user = current_user()
    if not user:
        raise RuntimeError("Not authenticated")
    sb = get_supabase()
    res = sb.table("documents").select("*").eq("user_id", user.id).order("version").execute()
    return res.data or []

def get_rewards_for_user() -> List[Dict[str, Any]]:
    user = current_user()
    if not user:
        raise RuntimeError("Not authenticated")
    sb = get_supabase()
    res = sb.table("reward_logs").select("*").eq("user_id", user.id).order("version").execute()
    return res.data or []
