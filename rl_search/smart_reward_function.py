import textstat
import language_tool_python
from sentence_transformers import SentenceTransformer, util

# ------------------------------
# Load embedding model once (cached)
# ------------------------------
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=".cache"   # works on local + Streamlit Cloud
)

# ------------------------------
# Use embedded LanguageTool (no external server needed)
# ------------------------------
tool = language_tool_python.LanguageTool("en-US")

# ------------------------------
# Compute Reward Function
# ------------------------------
def compute_reward(text, reference_text=None):
    """
    Compute reward metrics for a given text.

    Args:
        text (str): User's draft/content
        reference_text (str): Optional reference content for similarity

    Returns:
        dict: {score (float), similarity (float), readability (float), errors (int)}
    """

    # ------------------------------
    # Similarity (if reference available)
    # ------------------------------
    similarity_score = 0.0
    if reference_text:
        try:
            embedding1 = model.encode(reference_text, convert_to_tensor=True)
            embedding2 = model.encode(text, convert_to_tensor=True)
            similarity_score = float(util.cos_sim(embedding1, embedding2).item() or 0.0)
        except Exception as e:
            print(f"Embedding similarity error: {e}")
            similarity_score = 0.0

    # ------------------------------
    # Readability
    # ------------------------------
    try:
        readability_score = float(textstat.flesch_reading_ease(text))
    except Exception as e:
        print(f"Readability computation error: {e}")
        readability_score = 0.0

    # ------------------------------
    # Grammar errors
    # ------------------------------
    try:
        grammar_matches = tool.check(text)
        grammar_errors = int(len(grammar_matches))
    except Exception as e:
        print(f"LanguageTool error: {e}")
        grammar_errors = 0

    # ------------------------------
    # Final weighted score
    # ------------------------------
    final_score = float(
        (similarity_score * 0.9) + (readability_score * 0.9) - (grammar_errors * 0.3)
    )

    return {
        "score": round(final_score, 3),
        "similarity": round(similarity_score, 3),
        "readability": round(readability_score, 3),
        "errors": grammar_errors
    }
