import json
import chromadb
from chromadb.utils import embedding_functions

# =========================================================
# CONFIG
# =========================================================

COLLECTION_NAME = "shl_assessments"
CHROMA_PATH = "./chroma_db"
DATA_PATH = "data/shl_catalog.json"

# =========================================================
# EMBEDDING MODEL
# =========================================================

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

# =========================================================
# CATEGORY ALIASES
# =========================================================

CATEGORY_ALIASES = {
    "Ability & Aptitude": [
        "cognitive ability",
        "reasoning test",
        "aptitude testing",
        "problem solving",
        "analytical thinking",
        "logical reasoning",
        "numerical reasoning",
        "verbal reasoning"
    ],

    "Personality & Behavior": [
        "personality assessment",
        "behavioral assessment",
        "leadership style",
        "workplace behavior",
        "team behavior",
        "motivation",
        "communication style"
    ],

    "Knowledge & Skills": [
        "technical assessment",
        "coding test",
        "technical skills",
        "programming assessment",
        "domain expertise",
        "software engineering"
    ],

    "Competencies": [
        "competency assessment",
        "leadership competencies",
        "managerial effectiveness",
        "professional competencies"
    ],

    "Assessment Exercises": [
        "simulation exercise",
        "role play",
        "scenario assessment",
        "situational evaluation",
        "behavior simulation"
    ]
}

# =========================================================
# DOCUMENT TYPE DETECTION
# =========================================================

def detect_document_type(name):

    name = name.lower()

    # ---------------------------------------------------
    # REPORTS
    # ---------------------------------------------------

    report_keywords = [
        "report",
        "profile",
        "guide",
        "cards",
        "development report",
        "candidate report",
        "narrative report",
        "selection report"
    ]

    for keyword in report_keywords:
        if keyword in name:
            return "report"

    # ---------------------------------------------------
    # SIMULATIONS
    # ---------------------------------------------------

    simulation_keywords = [
        "simulation",
        "scenarios",
        "live coding",
        "smart interview"
    ]

    for keyword in simulation_keywords:
        if keyword in name:
            return "simulation"

    # ---------------------------------------------------
    # QUESTIONNAIRES
    # ---------------------------------------------------

    questionnaire_keywords = [
        "questionnaire",
        "opq",
        "mq"
    ]

    for keyword in questionnaire_keywords:
        if keyword in name:
            return "assessment"

    return "assessment"

# =========================================================
# SKILL ENRICHMENT
# =========================================================

def generate_skill_keywords(item):

    name = item.get("name", "").lower()
    description = item.get("description", "").lower()

    keywords = []

    # =====================================================
    # SOFTWARE ENGINEERING
    # =====================================================

    software_keywords = [
        "java", "python", "c#", "c++", "javascript",
        "react", "angular", "node", "spring",
        "django", "php", "ruby", "sql",
        "dotnet", ".net", "c programming",
        "programming", "development"
    ]

    if any(k in name for k in software_keywords):

        keywords.extend([
            "software engineer",
            "backend developer",
            "frontend developer",
            "full stack developer",
            "technical hiring",
            "coding assessment",
            "programming skills",
            "developer assessment",
            "software development",
            "technical screening"
        ])

    # =====================================================
    # JAVA
    # =====================================================

    if "java" in name:

        keywords.extend([
            "java developer",
            "spring boot",
            "object oriented programming",
            "enterprise applications",
            "backend systems"
        ])

    # =====================================================
    # PYTHON / DATA SCIENCE
    # =====================================================

    if (
        "python" in name or
        "data science" in name or
        "r programming" in name or
        "statistics" in name or
        "ai skills" in name
    ):

        keywords.extend([
            "machine learning",
            "data scientist",
            "analytics",
            "ai engineer",
            "statistical analysis",
            "data analysis",
            "data engineering"
        ])

    # =====================================================
    # CLOUD / DEVOPS
    # =====================================================

    cloud_keywords = [
        "aws",
        "docker",
        "kubernetes",
        "jenkins",
        "linux",
        "cloud"
    ]

    if any(k in name for k in cloud_keywords):

        keywords.extend([
            "devops engineer",
            "cloud engineer",
            "platform engineer",
            "infrastructure engineer",
            "deployment automation",
            "server infrastructure",
            "high performance systems"
        ])

    # =====================================================
    # NETWORKING
    # =====================================================

    if (
        "network" in name or
        "telecommunication" in name or
        "linux programming" in name
    ):

        keywords.extend([
            "network engineer",
            "systems engineering",
            "distributed systems",
            "tcp ip",
            "network infrastructure",
            "backend infrastructure",
            "server engineering"
        ])

    # =====================================================
    # CYBER SECURITY
    # =====================================================

    if (
        "cyber" in name or
        "security" in name
    ):

        keywords.extend([
            "cyber security",
            "information security",
            "risk management",
            "security analyst",
            "threat analysis"
        ])

    # =====================================================
    # RPA / AUTOMATION
    # =====================================================

    if (
        "uipath" in name or
        "automation anywhere" in name or
        "automata" in name
    ):

        keywords.extend([
            "robotic process automation",
            "automation engineer",
            "workflow automation",
            "rpa developer"
        ])

    # =====================================================
    # SALES / CUSTOMER SERVICE
    # =====================================================

    sales_keywords = [
        "sales",
        "customer service",
        "contact center",
        "retail"
    ]

    if any(k in name for k in sales_keywords):

        keywords.extend([
            "sales hiring",
            "customer support",
            "client interaction",
            "communication skills",
            "service orientation",
            "customer handling"
        ])

    # =====================================================
    # LEADERSHIP
    # =====================================================

    leadership_keywords = [
        "leadership",
        "managerial",
        "executive",
        "hipo",
        "management"
    ]

    if (
        any(k in name for k in leadership_keywords)
        or "leadership" in description
    ):

        keywords.extend([
            "executive hiring",
            "senior leadership",
            "leadership assessment",
            "cxo hiring",
            "director hiring",
            "manager assessment",
            "strategic thinking",
            "people management"
        ])

    # =====================================================
    # OPQ / PERSONALITY
    # =====================================================

    if (
        "opq" in name or
        "personality" in description or
        "motivation" in name
    ):

        keywords.extend([
            "personality assessment",
            "behavioral assessment",
            "workplace personality",
            "team fit",
            "leadership personality",
            "motivation analysis",
            "behavior profiling"
        ])

    # =====================================================
    # COGNITIVE / VERIFY
    # =====================================================

    if (
        "verify" in name or
        "reasoning" in name or
        "ability" in name or
        "aptitude" in description
    ):

        keywords.extend([
            "cognitive ability",
            "reasoning assessment",
            "general intelligence",
            "critical thinking",
            "problem solving",
            "analytical reasoning",
            "manager aptitude",
            "executive aptitude"
        ])

    # -----------------------------------------------------
    # VERIFY G+
    # -----------------------------------------------------

    if "g+" in name:

        keywords.extend([
            "general cognitive ability",
            "overall reasoning ability",
            "managerial reasoning",
            "executive reasoning",
            "multi aptitude assessment"
        ])

    # =====================================================
    # COMMUNICATION
    # =====================================================

    communication_keywords = [
        "spoken",
        "written",
        "communication",
        "email writing",
        "english"
    ]

    if any(k in name for k in communication_keywords):

        keywords.extend([
            "business communication",
            "verbal communication",
            "written communication",
            "email communication",
            "professional communication",
            "english proficiency"
        ])

    # =====================================================
    # FINANCE
    # =====================================================

    finance_keywords = [
        "accounting",
        "banking",
        "finance",
        "accounts payable",
        "accounts receivable"
    ]

    if any(k in name for k in finance_keywords):

        keywords.extend([
            "finance hiring",
            "accounting assessment",
            "financial operations",
            "banking domain",
            "accounts management"
        ])

    # =====================================================
    # HEALTHCARE
    # =====================================================

    healthcare_keywords = [
        "nursing",
        "medical",
        "pharma",
        "biology",
        "health"
    ]

    if any(k in name for k in healthcare_keywords):

        keywords.extend([
            "healthcare hiring",
            "clinical knowledge",
            "medical assessment",
            "healthcare professional",
            "patient care"
        ])

    # =====================================================
    # SIMULATIONS
    # =====================================================

    if (
        "simulation" in name or
        "scenarios" in name or
        "smart interview" in name
    ):

        keywords.extend([
            "situational judgement",
            "real world simulation",
            "job simulation",
            "behavioral simulation",
            "practical assessment"
        ])

    return list(set(keywords))

# =========================================================
# CREATE ENRICHED EMBEDDING TEXT
# =========================================================

def create_embedding_text(item):

    keys = item.get("keys", [])
    aliases = []

    for key in keys:
        aliases.extend(CATEGORY_ALIASES.get(key, []))

    generated_keywords = generate_skill_keywords(item)

    document_type = detect_document_type(item.get("name", ""))

    return f"""
    Assessment Name:
    {item.get("name", "")}

    Document Type:
    {document_type}

    Description:
    {item.get("description", "")}

    Assessment Categories:
    {", ".join(keys)}

    Related Assessment Concepts:
    {", ".join(aliases)}

    Additional Relevant Skills and Use Cases:
    {", ".join(generated_keywords)}

    Suitable Job Levels:
    {", ".join(item.get("job_levels", []))}

    Supported Languages:
    {", ".join(item.get("languages", []))}

    Duration:
    {item.get("duration", "")}

    Remote Testing Support:
    {item.get("remote", "")}

    Adaptive Testing:
    {item.get("adaptive", "")}

    SHL Catalog URL:
    {item.get("link", "")}
    """.strip().lower()

# =========================================================
# INGESTION
# =========================================================

def ingest():

    print("\nStarting ingestion process...\n")

    # -----------------------------------------------------
    # DELETE OLD COLLECTION
    # -----------------------------------------------------

    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except:
        print("No existing collection found.")

    # -----------------------------------------------------
    # CREATE NEW COLLECTION
    # -----------------------------------------------------

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )

    print(f"Created collection: {COLLECTION_NAME}\n")

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    ids = []
    documents = []
    metadatas = []

    total = len(data)

    # -----------------------------------------------------
    # PROCESS DOCUMENTS
    # -----------------------------------------------------

    for idx, item in enumerate(data, start=1):

        print(f"[{idx}/{total}] Processing: {item.get('name')}")

        document_type = detect_document_type(
            item.get("name", "")
        )

        embedding_text = create_embedding_text(item)

        metadata = {
            "name": item.get("name", ""),
            "url": item.get("link", ""),
            "description": item.get("description", ""),
            "keys": ",".join(item.get("keys", [])),
            "job_levels": ",".join(item.get("job_levels", [])),
            "languages": ",".join(item.get("languages", [])),
            "duration": item.get("duration", ""),
            "remote": item.get("remote", ""),
            "adaptive": item.get("adaptive", ""),
            "document_type": document_type
        }

        ids.append(str(item["entity_id"]))
        documents.append(embedding_text)
        metadatas.append(metadata)

    # -----------------------------------------------------
    # ADD TO COLLECTION
    # -----------------------------------------------------

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    # -----------------------------------------------------
    # DONE
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print(f"Successfully ingested {len(ids)} assessments.")
    print("=" * 60)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    ingest()