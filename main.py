import subprocess
import time
from chromadb_store import store_version
from rl_search_algorithm import select_best_version

def run_scraper():
    print("🕸️ Running scraper...")
    subprocess.run(["python", "playwright_scraper.py"])

def run_ai_writer():
    print("✍️ Running AI Writer...")
    subprocess.run(["python", "spin_writer_ollama.py"])

def run_human_editor():
    print("📝 Launching Human-in-the-Loop Editor...")
    subprocess.run(["streamlit", "run", "human_loop_editor_ui.py"])

def store_final_version():
    with open("output/finalversion.txt", "r", encoding="utf-8") as f:
        final_content = f.read()
    version_num = int(time.time())  # unique version based on timestamp
    store_version(final_content, version_num)

def run_search_algorithm():
    print("🔍 Retrieving best version...")
    select_best_version()

if __name__ == "__main__":
    run_scraper()
    run_ai_writer()

    print("✅ Scraper and AI Writer done.\n")
    input("👉 Press Enter after Human-in-the-Loop editing is completed...")

    select_best_version()
    print("✅ Final version stored in ChromaDB.\n")

    run_search_algorithm()

