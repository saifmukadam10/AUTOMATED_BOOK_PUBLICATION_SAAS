import re
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer, util

# 🔹 Lazy import of language_tool_python (avoids Java crash at startup)
try:
    import language_tool_python
    tool = language_tool_python.LanguageTool('en-US')
    corrections = tool.check("This are wrong sentence.")
except Exception as e:
    print(f"[Warning] Grammar tool unavailable: {e}")
    tool = None

# 🔹 Embedding Model for plagiarism
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# ----------------- Grammar + Style -----------------
def correct_grammar_and_style(text: str) -> str:
    """Correct grammar and style using LanguageTool."""
    if not text.strip():
        return "⚠️ No text provided."

    if tool is None:
        return "⚠️ Grammar tool unavailable (Java not installed)."

    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text


# ----------------- Keyword Extraction -----------------
def extract_keywords(text: str, top_n: int = 10) -> list:
    """Extract top keywords from text for SEO optimization."""
    if not text.strip():
        return []

    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
    vectorizer = CountVectorizer(stop_words="english").fit([cleaned])
    bag = vectorizer.transform([cleaned])
    word_freq = zip(vectorizer.get_feature_names_out(), bag.toarray()[0])

    sorted_words = sorted(word_freq, key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:top_n]]
    return keywords


# ----------------- Plagiarism Check -----------------
def check_plagiarism(text: str, references: list = None) -> dict:
    """
    Basic plagiarism check by comparing against reference texts.
    Replace with Copyleaks/Turnitin API for production.
    """
    if not text.strip():
        return {"status": "error", "message": "No text provided."}

    if not references:
        references = [
            "This is a sample reference text stored in the database.",
            "AI is transforming the world with NLP and machine learning."
        ]

    embedding = model.encode(text, convert_to_tensor=True)
    similarities = []

    for ref in references:
        ref_emb = model.encode(ref, convert_to_tensor=True)
        sim_score = util.cos_sim(embedding, ref_emb).item()
        similarities.append({"reference": ref, "similarity": sim_score})

    max_match = max(similarities, key=lambda x: x["similarity"])

    return {
        "status": "success",
        "highest_match": max_match,
        "all_matches": similarities
    }
