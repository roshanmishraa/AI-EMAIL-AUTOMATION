from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Literal
from app.core.config import settings


# -----------------------------
# OUTPUT SCHEMA
# -----------------------------
class SentimentResult(BaseModel):
    sentiment: Literal["angry", "frustrated", "neutral", "happy", "sad"]

    intent: Literal[
        "urgent_resolution",
        "info_request",
        "escalation_threat",
        "repeat_complaint",
        "general"
    ]

    is_vip_signal: bool
    urgency_score: float  # 0-100


# -----------------------------
# PROMPT (CLEAN + ROBUST)
# -----------------------------
SENTIMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are a customer support sentiment + intent analyzer.

Analyze the email and return:

- sentiment
- intent
- VIP signal (true/false)
- urgency score (0-100)

Rules:
- Be accurate
- VIP signal if customer sounds high value or repeated complaints
- urgency score based on emotional intensity

Return structured output only.
"""),
    ("human", "{body}")
])


# -----------------------------
# LLM INIT
# -----------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=settings.OPENAI_API_KEY,
)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
async def detect_sentiment(body: str) -> SentimentResult:
    """
    Returns sentiment + intent + urgency signals for email.
    """

    structured_llm = llm.with_structured_output(SentimentResult)

    chain = SENTIMENT_PROMPT | structured_llm

    result = await chain.ainvoke({
        "body": body
    })

    return result