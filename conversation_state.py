import re

# =========================================================
# STATE TEMPLATE
# =========================================================

def initialize_state():

    return {

        # -------------------------------------------------
        # ROLE / CONTEXT
        # -------------------------------------------------

        "role": None,

        "industry": None,

        "job_level": None,

        "seniority": None,

        "candidate_type": None,

        # -------------------------------------------------
        # SKILLS
        # -------------------------------------------------

        "skills": [],

        "secondary_skills": [],

        # -------------------------------------------------
        # REQUIREMENTS
        # -------------------------------------------------

        "assessment_types": [],

        "languages": [],

        "intent": None,

        # -------------------------------------------------
        # CONSTRAINTS
        # -------------------------------------------------

        "must_include": [],

        "must_exclude": [],

        # -------------------------------------------------
        # FLAGS
        # -------------------------------------------------

        "personality_required": False,

        "cognitive_required": False,

        "simulation_required": False,

        "development_required": False,

        "volume_hiring": False,

        # -------------------------------------------------
        # SYSTEM
        # -------------------------------------------------

        "clarification_needed": None
    }

# =========================================================
# HELPERS
# =========================================================

def add_unique(lst, value):

    value = value.lower().strip()

    if value and value not in lst:
        lst.append(value)

# =========================================================
# SAFE PHRASE MATCH
# =========================================================

def contains_phrase(text, phrase):

    pattern = rf"\b{re.escape(phrase.lower())}\b"

    return re.search(pattern, text) is not None

# =========================================================
# UPDATE STATE
# =========================================================

def update_state(state, user_message):

    text = user_message.lower()

    # =====================================================
    # ROLE DETECTION
    # =====================================================

    role_patterns = {

        "leadership": [
            "leadership",
            "executive",
            "director",
            "cxo",
            "vp",
            "vice president",
            "head of"
        ],

        "software engineer": [
            "software engineer",
            "developer",
            "backend engineer",
            "frontend engineer",
            "full stack",
            "programmer",
            "technical lead"
        ],

        "customer service": [
            "customer service",
            "contact center",
            "call center",
            "support representative",
            "customer support"
        ],

        "financial analyst": [
            "financial analyst",
            "finance analyst",
            "accounting role",
            "finance professional"
        ],

        "healthcare admin": [
            "healthcare admin",
            "medical admin",
            "patient records",
            "clinical support"
        ],

        "administrative assistant": [
            "admin assistant",
            "administrative assistant",
            "office assistant",
            "clerical"
        ],

        "industrial operator": [
            "plant operator",
            "industrial worker",
            "manufacturing operator",
            "chemical operator"
        ]
    }

    for role, patterns in role_patterns.items():

        if any(
            contains_phrase(text, p)
            for p in patterns
        ):

            if not state["role"]:
                state["role"] = role
            break

    # =====================================================
    # INDUSTRY DETECTION
    # =====================================================

    industry_patterns = {

        "technology": [
            "software",
            "cloud",
            "aws",
            "developer",
            "engineering"
        ],

        "finance": [
            "finance",
            "financial",
            "accounting",
            "banking"
        ],

        "healthcare": [
            "healthcare",
            "medical",
            "clinical",
            "hipaa",
            "patient"
        ],

        "manufacturing": [
            "manufacturing",
            "industrial",
            "chemical",
            "plant",
            "safety"
        ],

        "customer service": [
            "contact center",
            "call center",
            "customer support",
            "inbound calls"
        ]
    }

    for industry, patterns in industry_patterns.items():

        if any(
            contains_phrase(text, p)
            for p in patterns
        ):

            state["industry"] = industry
            break

    # =====================================================
    # SENIORITY
    # =====================================================

    if any(
        contains_phrase(text, x)
        for x in [
            "senior",
            "lead",
            "principal",
            "staff engineer",
            "experienced"
        ]
    ):

        state["seniority"] = "senior"

    elif any(
        contains_phrase(text, x)
        for x in [
            "junior",
            "entry level",
            "entry-level"
        ]
    ):

        state["seniority"] = "junior"

    # =====================================================
    # CANDIDATE TYPE
    # =====================================================

    if any(
        contains_phrase(text, x)
        for x in [
            "graduate",
            "campus hiring",
            "final-year",
            "student",
            "graduate trainee"
        ]
    ):

        state["candidate_type"] = "graduate"

    elif any(
        contains_phrase(text, x)
        for x in [
            "entry-level",
            "entry level"
        ]
    ):

        state["candidate_type"] = "entry-level"

    # =====================================================
    # INTENT
    # =====================================================

    if any(
        contains_phrase(text, x)
        for x in [
            "selection",
            "hiring",
            "screening",
            "evaluate candidates"
        ]
    ):

        state["intent"] = "selection"

    if any(
        contains_phrase(text, x)
        for x in [
            "development",
            "developmental",
            "coaching",
            "feedback"
        ]
    ):

        state["intent"] = "development"

        state["development_required"] = True

    # =====================================================
    # IMPORTANT SIGNALS
    # =====================================================

    important_signals = [

        "benchmark",

        "safety",

        "compliance",

        "reliability",

        "customer interaction",

        "people management",

        "strategic thinking",

        "patient records",

        "bilingual",

        "high performance"
    ]

    for signal in important_signals:

        if contains_phrase(text, signal):

            add_unique(
                state["must_include"],
                signal
            )

    # =====================================================
    # ASSESSMENT TYPE DETECTION
    # =====================================================

    personality_terms = [

        "personality",

        "behavior",

        "behavioral",

        "culture fit",

        "leadership style",

        "opq"
    ]

    if any(
        contains_phrase(text, x)
        for x in personality_terms
    ):

        state["personality_required"] = True

    cognitive_terms = [

        "cognitive",

        "reasoning",

        "aptitude",

        "numerical",

        "verbal",

        "analytical",

        "problem solving",

        "verify"
    ]

    if any(
        contains_phrase(text, x)
        for x in cognitive_terms
    ):

        state["cognitive_required"] = True

    simulation_terms = [

        "simulation",

        "situational",

        "scenario",

        "role play",

        "practical assessment"
    ]

    if any(
        contains_phrase(text, x)
        for x in simulation_terms
    ):

        state["simulation_required"] = True

    # =====================================================
    # SKILL DETECTION
    # =====================================================

    skill_groups = {

        # -------------------------------------------------
        # SOFTWARE
        # -------------------------------------------------

        "java": [
            "java",
            "core java"
        ],

        "spring": [
            "spring",
            "spring boot"
        ],

        "sql": [
            "sql",
            "mysql",
            "postgresql"
        ],

        "aws": [
            "aws",
            "amazon web services"
        ],

        "docker": [
            "docker"
        ],

        "angular": [
            "angular"
        ],

        "rest": [
            "rest",
            "rest api"
        ],

        "python": [
            "python"
        ],

        "linux": [
            "linux"
        ],

        "networking": [
            "networking",
            "network infrastructure",
            "telecommunications"
        ],

        "rust": [
            "rust"
        ],

        # -------------------------------------------------
        # OFFICE / ADMIN
        # -------------------------------------------------

        "excel": [
            "excel"
        ],

        "word": [
            "word"
        ],

        # -------------------------------------------------
        # BUSINESS
        # -------------------------------------------------

        "sales": [
            "sales"
        ],

        "customer service": [
            "customer service",
            "customer support",
            "contact center"
        ],

        # -------------------------------------------------
        # FINANCE
        # -------------------------------------------------

        "finance": [
            "finance",
            "financial"
        ],

        "accounting": [
            "accounting"
        ],

        "numerical reasoning": [
            "numerical reasoning"
        ],

        # -------------------------------------------------
        # HEALTHCARE
        # -------------------------------------------------

        "hipaa": [
            "hipaa"
        ]
    }

    for canonical_skill, aliases in skill_groups.items():

        if any(
            contains_phrase(text, alias)
            for alias in aliases
        ):

            add_unique(
                state["skills"],
                canonical_skill
            )

    # =====================================================
    # EXCLUSION HANDLING
    # =====================================================

    exclusion_patterns = [

        r"drop ([a-zA-Z0-9+ ]+)",

        r"remove ([a-zA-Z0-9+ ]+)",

        r"exclude ([a-zA-Z0-9+ ]+)",

        r"without ([a-zA-Z0-9+ ]+)"
    ]

    for pattern in exclusion_patterns:

        matches = re.findall(pattern, text)

        for match in matches:

            add_unique(
                state["must_exclude"],
                match.strip()
            )

    # =====================================================
    # LANGUAGE DETECTION
    # =====================================================

    supported_languages = [

        "english",

        "spanish",

        "french",

        "german",

        "us",

        "uk"
    ]

    for lang in supported_languages:

        if contains_phrase(text, lang):

            add_unique(
                state["languages"],
                lang
            )

    # =====================================================
    # VOLUME HIRING
    # =====================================================

    volume_patterns = [

        "high-volume",

        "mass hiring",

        "bulk hiring",

        "500",

        "1000",

        "large scale hiring",

        "screening hundreds"
    ]

    if any(
        contains_phrase(text, x)
        for x in volume_patterns
    ):

        state["volume_hiring"] = True

    # =====================================================
    # ROLE-BASED DEFAULTS
    # =====================================================

    if state["role"] == "leadership":

        state["personality_required"] = True

    if state["role"] in [

        "software engineer",

        "financial analyst"
    ]:

        state["cognitive_required"] = True

    # =====================================================
    # REMOVE EXCLUDED SKILLS
    # =====================================================

    cleaned_skills = []

    for skill in state["skills"]:

        blocked = False

        for excluded in state["must_exclude"]:

            if excluded.lower() in skill.lower():

                blocked = True
                break

        if not blocked:

            cleaned_skills.append(skill)

    state["skills"] = cleaned_skills

    return state