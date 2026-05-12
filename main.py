# =========================================================
# main.py
# FASTAPI ENTRYPOINT FOR SHL AGENT
# =========================================================

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from agent import agent_reply

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="SHL Conversational Assessment Recommender",
    version="1.0.0"
)

# =========================================================
# REQUEST / RESPONSE SCHEMA
# =========================================================

class Message(BaseModel):

    role: str
    content: str


class ChatRequest(BaseModel):

    messages: List[Message]


class Recommendation(BaseModel):

    name: str
    url: str
    document_type: Optional[str] = ""
    duration: Optional[str] = ""


class ChatResponse(BaseModel):

    reply: str
    recommendations: Optional[List[Recommendation]] = None
    end_of_conversation: bool


# =========================================================
# HEALTH ENDPOINT
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# CHAT ENDPOINT
# =========================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        # -------------------------------------------------
        # CONVERT TO DICT FORMAT
        # -------------------------------------------------

        messages = [

            {
                "role": msg.role,
                "content": msg.content
            }

            for msg in request.messages
        ]

        # -------------------------------------------------
        # AGENT RESPONSE
        # -------------------------------------------------

        result = agent_reply(messages)

        # =========================================================
        # FORMAT RECOMMENDATIONS
        # =========================================================

        formatted_recommendations = []

        if result.get("recommendations"):

            for item in result["recommendations"]:

                if not item.get("url"):
                    continue

                formatted_recommendations.append({

                    "name": item.get("name", ""),

                    "url": item.get("url", ""),

                    "document_type": item.get(
                        "document_type",
                        ""
                    ),

                    "duration": item.get(
                        "duration",
                        ""
                    )
                })

        # =========================================================
        # RETURN RESPONSE
        # =========================================================

        return {

            "reply": str(
                result.get("reply", "")
            ),

            "recommendations":
            formatted_recommendations,

            "end_of_conversation": bool(
                result.get(
                    "end_of_conversation",
                    False
                )
            )
        }

    except Exception as e:

        return {

            "reply": f"Internal server error: {str(e)}",

            "recommendations": [],

            "end_of_conversation": False
        }


# =========================================================
# LOCAL RUN
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )