from conversation_state import (
    initialize_state,
    update_state
)

# =========================================================
# HELPERS
# =========================================================

def add_query_parts(query_parts, values):

    for value in values:

        if value and value not in query_parts:

            query_parts.append(value)

# =========================================================
# BUILD SEARCH QUERY
# =========================================================

def build_search_query(messages):

    # =====================================================
    # BUILD CONVERSATION STATE
    # =====================================================

    state = initialize_state()

    for msg in messages:

        if msg["role"] == "user":

            state = update_state(
                state,
                msg["content"]
            )

    # =====================================================
    # QUERY PARTS
    # =====================================================

    query_parts = []

    # =====================================================
    # CORE CONTEXT
    # =====================================================

    core_fields = [

        state["role"],

        state["industry"],

        state["job_level"],

        state["seniority"],

        state["intent"]
    ]

    add_query_parts(
        query_parts,
        [x for x in core_fields if x]
    )

    # =====================================================
    # SKILLS / LANGUAGES
    # =====================================================

    add_query_parts(
        query_parts,
        state["skills"]
    )

    add_query_parts(
        query_parts,
        state["secondary_skills"]
    )

    add_query_parts(
        query_parts,
        state["languages"]
    )

    # =====================================================
    # MUST INCLUDE
    # =====================================================

    add_query_parts(
        query_parts,
        state["must_include"]
    )

    # =====================================================
    # PERSONALITY ENRICHMENT
    # =====================================================

    if state["personality_required"]:

        add_query_parts(query_parts, [

            "opq32r",

            "personality assessment",

            "behavioral assessment",

            "workplace personality",

            "leadership behavior"
        ])

    # =====================================================
    # COGNITIVE ENRICHMENT
    # =====================================================

    if state["cognitive_required"]:

        add_query_parts(query_parts, [

            "verify g+",

            "cognitive ability",

            "reasoning assessment",

            "analytical thinking",

            "problem solving"
        ])

    # =====================================================
    # SIMULATION ENRICHMENT
    # =====================================================

    if state["simulation_required"]:

        add_query_parts(query_parts, [

            "simulation",

            "situational judgement",

            "job scenarios",

            "practical assessment"
        ])

    # =====================================================
    # DEVELOPMENT ENRICHMENT
    # =====================================================

    if state["development_required"]:

        add_query_parts(query_parts, [

            "development report",

            "development feedback",

            "leadership development"
        ])

    # =====================================================
    # VOLUME HIRING
    # =====================================================

    if state["volume_hiring"]:

        add_query_parts(query_parts, [

            "high volume hiring",

            "mass screening",

            "entry level screening"
        ])

    # =====================================================
    # CANDIDATE TYPE
    # =====================================================

    if state["candidate_type"] == "graduate":

        add_query_parts(query_parts, [

            "graduate hiring",

            "graduate scenarios",

            "entry level reasoning"
        ])

    elif state["candidate_type"] == "entry-level":

        add_query_parts(query_parts, [

            "entry level",

            "customer interaction",

            "service orientation"
        ])

    # =====================================================
    # DOMAIN ENRICHMENT
    # =====================================================

    # -----------------------------------------------------
    # CONTACT CENTER / CUSTOMER SERVICE
    # -----------------------------------------------------

    if (
        state["industry"] == "customer service"
        or "customer service" in state["skills"]
    ):

        add_query_parts(query_parts, [

            "contact center",

            "call center simulation",

            "spoken english",

            "customer support",

            "inbound calls"
        ])

    # -----------------------------------------------------
    # HEALTHCARE
    # -----------------------------------------------------

    if state["industry"] == "healthcare":

        add_query_parts(query_parts, [

            "healthcare administration",

            "patient records",

            "medical compliance",

            "clinical support"
        ])

    # -----------------------------------------------------
    # FINANCE
    # -----------------------------------------------------

    if state["industry"] == "finance":

        add_query_parts(query_parts, [

            "financial accounting",

            "numerical reasoning",

            "finance assessment",

            "financial analysis"
        ])

    # -----------------------------------------------------
    # INDUSTRIAL / MANUFACTURING
    # -----------------------------------------------------

    if (
        state["industry"] == "manufacturing"
        or "safety" in state["must_include"]
    ):

        add_query_parts(query_parts, [

            "workplace safety",

            "dependability",

            "industrial assessment",

            "manufacturing safety"
        ])

    # -----------------------------------------------------
    # NETWORKING / INFRASTRUCTURE
    # -----------------------------------------------------

    infrastructure_skills = [

        "networking",

        "linux",

        "rust"
    ]

    if any(
        skill in state["skills"]
        for skill in infrastructure_skills
    ):

        add_query_parts(query_parts, [

            "linux programming",

            "systems engineering",

            "network infrastructure",

            "server engineering"
        ])

    # -----------------------------------------------------
    # ADMINISTRATION
    # -----------------------------------------------------

    admin_skills = [

        "excel",

        "word"
    ]

    if any(
        skill in state["skills"]
        for skill in admin_skills
    ):

        add_query_parts(query_parts, [

            "administrative assistant",

            "office administration",

            "clerical assessment"
        ])

    # =====================================================
    # REMOVE EXCLUDED TERMS
    # =====================================================

    filtered_parts = []

    for item in query_parts:

        blocked = False

        for excluded in state["must_exclude"]:

            if excluded.lower() in item.lower():

                blocked = True
                break

        if not blocked:

            filtered_parts.append(
                item.strip().lower()
            )

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    final_parts = []

    seen = set()

    for item in filtered_parts:

        if item and item not in seen:

            seen.add(item)

            final_parts.append(item)

    # =====================================================
    # FINAL QUERY
    # =====================================================

    search_query = " ".join(final_parts)

    # =====================================================
    # CLARIFICATION LOGIC
    # =====================================================

    needs_clarification = False

    clarification_question = None

    # -----------------------------------------------------
    # LEADERSHIP CLARIFICATION
    # -----------------------------------------------------

    if (

        state["role"] == "leadership"

        and not state["intent"]

    ):

        needs_clarification = True

        clarification_question = (
            "Is this for selection or leadership development?"
        )

    # -----------------------------------------------------
    # TECHNICAL SENIORITY CLARIFICATION
    # -----------------------------------------------------

    technical_skills = [

        "java",

        "python",

        "aws",

        "docker",

        "spring",

        "sql",

        "linux",

        "networking",

        "rust"
    ]

    requires_seniority = any(
        skill in state["skills"]
        for skill in technical_skills
    )

    if (

        requires_seniority

        and not state["seniority"]

        and state["candidate_type"] not in [

            "graduate",

            "entry-level"
        ]

    ):

        needs_clarification = True

        clarification_question = (
            "What seniority level is the role?"
        )

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "state": state,

        "search_query": search_query,

        "needs_clarification": needs_clarification,

        "clarification_question": clarification_question
    }