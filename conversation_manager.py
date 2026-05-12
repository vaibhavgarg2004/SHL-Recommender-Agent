import os

from dotenv import load_dotenv
from groq import Groq

from query_builder import build_search_query
from retriever import recommend

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# GROQ CLIENT
# =========================================================

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

GROQ_MODEL = os.environ.get(
    "GROQ_MODEL",
    "llama-3.1-8b-instant"
)

# =========================================================
# HELPERS
# =========================================================

def get_last_user_message(messages):

    for msg in reversed(messages):

        if msg["role"] == "user":

            return msg["content"]

    return ""

# =========================================================
# CONVERSATION COMPLETION
# =========================================================

def is_conversation_complete(user_text):

    user_text = user_text.lower()

    completion_phrases = [

        "perfect",

        "looks good",

        "that's what we need",

        "this works",

        "great",

        "thank you",

        "thanks",

        "done",

        "finalize"
    ]

    return any(
        phrase in user_text
        for phrase in completion_phrases
    )

# =========================================================
# FILTER RECOMMENDATIONS
# =========================================================

def filter_recommendations(results):

    if not results:
        return []

    filtered = []

    noisy_terms = [

        "profile report",

        "development report",

        "development feedback"
    ]

    for item in results:

        name = item.get(
            "name",
            ""
        ).lower()

        if any(
            term in name
            for term in noisy_terms
        ):
            continue

        filtered.append(item)

    return filtered

# =========================================================
# DETECT MISSING SKILL COVERAGE
# =========================================================

def detect_missing_skill_coverage(

    state,
    recommendations
):

    if not recommendations:
        return []

    user_skills = set(

        skill.lower()
        for skill in state.get(
            "skills",
            []
        )
    )

    if not user_skills:
        return []

    recommendation_text = ""

    for item in recommendations:

        recommendation_text += " "

        recommendation_text += item.get(
            "name",
            ""
        ).lower()

        recommendation_text += " "

        recommendation_text += item.get(
            "description",
            ""
        ).lower()

    missing = []

    for skill in user_skills:

        if skill not in recommendation_text:

            missing.append(skill)

    return missing

# =========================================================
# FORMAT CANDIDATES FOR PROMPT
# =========================================================

def format_candidates_for_prompt(results):

    if not results:
        return "No recommendations available."

    formatted = []

    for idx, item in enumerate(results, start=1):

        formatted.append(

            f"""
Assessment {idx}

Name:
{item.get("name", "")}

Document Type:
{item.get("document_type", "")}

Description:
{item.get("description", "")}

Job Levels:
{item.get("job_levels", "")}

Duration:
{item.get("duration", "")}

URL:
{item.get("url", "")}
""".strip()
        )

    return "\n\n".join(formatted)

# =========================================================
# GENERATE LLM RESPONSE
# =========================================================

def generate_agent_response(

    messages,
    state,
    recommendations,
    missing_skills=None,
    clarification_needed=False,
    clarification_question=None,
    conversation_complete=False
):

    formatted_recommendations = (
        format_candidates_for_prompt(
            recommendations
        )
    )

    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    system_prompt = """
You are an expert SHL assessment recommendation consultant.

Guidelines:
- Help recruiters choose suitable SHL assessments.
- Maintain conversational continuity across turns.
- Be concise, confident, and consultative.
- Speak naturally and directly.
- Avoid repetitive or overly polite assistant phrasing.
- Ask clarification questions only when necessary.
- If enough context exists, provide recommendations confidently.
- Use only the retrieved recommendations.
- Never invent assessments or URLs.

Recommendation behavior:
- Prefer foundational assessments before related reports when relevant.
- Explain briefly why the recommendations fit the role or hiring goal.
- If some requested skills do not have exact assessment coverage,
  explain that naturally and recommend the closest alternatives.
- Keep responses compact and recruiter-focused.

Formatting:
- If recommendations are provided:
  - Show them as a numbered list.
  - Include:
    - Name
    - Document Type
    - Duration
    - URL

- If clarification is needed:
  - Ask a short natural follow-up question.

- If the conversation is complete:
  - Briefly summarize the recommendation logic and conclude professionally.
"""

    # =====================================================
    # USER PROMPT
    # =====================================================

    user_prompt = f"""
Conversation:
{messages}

Structured State:
{state}

Missing Skill Coverage:
{missing_skills}

Clarification Needed:
{clarification_needed}

Clarification Question:
{clarification_question}

Conversation Complete:
{conversation_complete}

Retrieved Recommendations:
{formatted_recommendations}

Generate the assistant response.
"""

    # =====================================================
    # LLM CALL
    # =====================================================

    try:

        completion = groq_client.chat.completions.create(

            model=GROQ_MODEL,

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.3
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:

        return f"Error generating response: {str(e)}"

# =========================================================
# MAIN CONVERSATION HANDLER
# =========================================================

def handle_conversation(messages):

    # =====================================================
    # LAST USER MESSAGE
    # =====================================================

    last_user_message = get_last_user_message(
        messages
    )

    # =====================================================
    # BUILD QUERY
    # =====================================================

    query_data = build_search_query(
        messages
    )

    state = query_data["state"]

    # =====================================================
    # CONVERSATION COMPLETE
    # =====================================================

    if is_conversation_complete(
        last_user_message
    ):

        response = generate_agent_response(

            messages=messages,

            state=state,

            recommendations=None,

            missing_skills=None,

            clarification_needed=False,

            clarification_question=None,

            conversation_complete=True
        )

        return {

            "reply": response,

            "recommendations": None,

            "end_of_conversation": True
        }

    # =====================================================
    # CLARIFICATION FLOW
    # =====================================================

    if query_data["needs_clarification"]:

        # -------------------------------------------------
        # LEADERSHIP FLOW
        # -------------------------------------------------

        if state["role"] == "leadership":

            if not state["seniority"]:

                return {

                    "reply":
                    "Happy to help narrow that down. Who is this meant for?",

                    "recommendations": None,

                    "end_of_conversation": False
                }

            return {

                "reply":
                (
                    "For senior leadership roles, OPQ32r is commonly used "
                    "to assess leadership style, influencing approach, "
                    "and workplace behaviour.\n\n"
                    "Is this for selection or leadership development?"
                ),

                "recommendations": None,

                "end_of_conversation": False
            }

        # -------------------------------------------------
        # DEFAULT FLOW
        # -------------------------------------------------

        response = generate_agent_response(

            messages=messages,

            state=state,

            recommendations=None,

            missing_skills=None,

            clarification_needed=True,

            clarification_question=query_data[
                "clarification_question"
            ],

            conversation_complete=False
        )

        return {

            "reply": response,

            "recommendations": None,

            "end_of_conversation": False
        }

    # =====================================================
    # RETRIEVE RECOMMENDATIONS
    # =====================================================

    recommendations = recommend(

        query_data["search_query"],

        n_results=7
    )

    # =====================================================
    # FILTER
    # =====================================================

    recommendations = filter_recommendations(
        recommendations
    )

    # =====================================================
    # DETECT COVERAGE GAPS
    # =====================================================

    missing_skills = detect_missing_skill_coverage(

        state,
        recommendations
    )

    # =====================================================
    # GENERATE RESPONSE
    # =====================================================

    response = generate_agent_response(

        messages=messages,

        state=state,

        recommendations=recommendations,

        missing_skills=missing_skills,

        clarification_needed=False,

        clarification_question=None,

        conversation_complete=False
    )

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "reply": response,

        "recommendations": recommendations,

        "end_of_conversation": False
    }