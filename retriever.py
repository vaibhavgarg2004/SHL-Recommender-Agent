import os
import json
import chromadb

from dotenv import load_dotenv
from groq import Groq

from chromadb.utils import embedding_functions

load_dotenv()

# =========================================================
# CONFIG
# =========================================================

COLLECTION_NAME = "shl_assessments"

# =========================================================
# CHROMA
# =========================================================

client = chromadb.PersistentClient(path="./chroma_db")

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=ef
)

# =========================================================
# GROQ
# =========================================================

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

GROQ_MODEL = os.environ.get(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

# =========================================================
# RAW RETRIEVAL
# =========================================================

def retrieve_candidates(search_query, n_results=40):

    results = collection.query(
        query_texts=[search_query],
        n_results=n_results
    )

    processed = []

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, distance in zip(
        docs,
        metas,
        distances
    ):

        processed.append({
            "document": doc,
            "metadata": meta,
            "distance": distance
        })

    return processed

# =========================================================
# RERANKING
# =========================================================

def rerank_results(query, candidates):

    reranked = []

    query = query.lower()

    for item in candidates:

        meta = item["metadata"]

        name = meta.get("name", "").lower()

        score = 1 / (1 + item["distance"])

        # -------------------------------------------------
        # DOCUMENT TYPE BOOSTS
        # -------------------------------------------------

        if meta.get("document_type") == "assessment":
            score += 0.15

        if meta.get("document_type") == "report":
            score -= 0.05

        # -------------------------------------------------
        # OPQ BOOST
        # -------------------------------------------------

        if "opq32r" in name:
            score += 0.15

        # -------------------------------------------------
        # VERIFY BOOST
        # -------------------------------------------------

        if "verify" in name:
            score += 0.08

        # -------------------------------------------------
        # JAVA BOOST
        # -------------------------------------------------

        if "java" in query and "java" in name:
            score += 0.15

        # -------------------------------------------------
        # PYTHON BOOST
        # -------------------------------------------------

        if "python" in query and "python" in name:
            score += 0.15

        # -------------------------------------------------
        # LEADERSHIP BOOST
        # -------------------------------------------------

        if any(word in query for word in [
            "leadership",
            "executive",
            "director",
            "manager"
        ]):

            if any(word in name for word in [
                "leadership",
                "opq"
            ]):
                score += 0.10

        # -------------------------------------------------
        # SENIORITY BOOST
        # -------------------------------------------------

        job_levels = meta.get("job_levels", "").lower()

        if "executive" in query and "executive" in job_levels:
            score += 0.08

        if "director" in query and "director" in job_levels:
            score += 0.08

        reranked.append({
            "score": score,
            "metadata": meta
        })

    reranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return reranked

# =========================================================
# DIVERSIFICATION
# =========================================================

def diversify_results(results, max_results=10):

    diversified = []

    report_count = 0

    seen_names = set()

    for item in results:

        meta = item["metadata"]

        name = meta.get("name")

        if name in seen_names:
            continue

        seen_names.add(name)

        # ---------------------------------------------
        # LIMIT REPORTS
        # ---------------------------------------------

        if meta.get("document_type") == "report":

            if report_count >= 2:
                continue

            report_count += 1

        diversified.append(meta)

        if len(diversified) >= max_results:
            break

    return diversified

# =========================================================
# OPTIONAL LLM REFINEMENT
# =========================================================

def llm_refine(query, candidates, top_k=10):

    formatted = "\n\n".join([

        f"""
Name: {c.get("name")}
Description: {c.get("description")}
Job Levels: {c.get("job_levels")}
Categories: {c.get("keys")}
URL: {c.get("url")}
"""

        for c in candidates
    ])

    prompt = f"""
You are an SHL assessment recommendation system.

Select the TOP {top_k} most relevant assessments.

Rules:
- ONLY use provided assessments
- Prefer foundational instruments over derivative reports
- Maintain assessment diversity
- Return ONLY valid JSON array of URLs

USER REQUIREMENT:
{query}

ASSESSMENTS:
{formatted}
"""

    try:

        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = completion.choices[0].message.content

        selected_urls = json.loads(content)

    except Exception:
        return candidates[:top_k]

    url_map = {
        c["url"]: c
        for c in candidates
    }

    final = []

    for url in selected_urls:

        if url in url_map:
            final.append(url_map[url])

    # Fill if fewer returned
    for c in candidates:

        if c not in final and len(final) < top_k:
            final.append(c)

    return final[:top_k]

# =========================================================
# PUBLIC RECOMMEND FUNCTION
# =========================================================

def recommend(search_query, n_results=10):

    # STEP 1
    candidates = retrieve_candidates(
        search_query,
        n_results=40
    )

    # STEP 2
    reranked = rerank_results(
        search_query,
        candidates
    )

    # STEP 3
    diversified = diversify_results(
        reranked,
        max_results=15
    )

    # STEP 4
    final_results = llm_refine(
        search_query,
        diversified,
        top_k=n_results
    )

    return final_results