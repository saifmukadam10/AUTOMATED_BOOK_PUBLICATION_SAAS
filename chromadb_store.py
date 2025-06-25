import chromadb
from chromadb.config import Settings
from datetime import datetime

client = chromadb.PersistentClient(path=".chroma_store")

collection = client.get_or_create_collection("chapter_versions")

# rest of your code as before...


def store_version(version_text, version_number):
    doc_id=f"version_{version_number}"
    metadata= {
        "version": version_number,
        "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    collection.add(
        ids=[doc_id],
        documents=[version_text],
        metadatas=[metadata]
    )

    print(f"✅ Stored version {version_number}")

def view_all_versions():
    results= collection.get(include=["documents","metadatas"])
    for doc,meta in zip(results['documents'],results['metadatas']):
        print(f"\n📄 Version {meta['version']} ({meta['date']}):\n{doc}\n")
    
if __name__ == "__main__":
    store_version("This is version 1 of Chapter 1.", 1)
    store_version("This is version 2 of Chapter 1 with improvements.", 2)
    view_all_versions()

  

