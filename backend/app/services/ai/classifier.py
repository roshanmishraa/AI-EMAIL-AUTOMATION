from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Literal
from app.core.config import settings


# -----------------------------
# OUTPUT SCHEMA
# -----------------------------
class ClassificationResult(BaseModel):
    category: Literal[
        "legal", "billing", "product_issue",
        "delivery", "refund", "general", "spam", "feedback"
    ]
    confidence: float  # 0-100
    reasoning: str


# -----------------------------
# PROMPT (SIMPLIFIED + ROBUST)
# -----------------------------
CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert customer support email classifier.

Classify the email into ONE category:

Categories:
- legal: lawsuits, GDPR, legal threats
- billing: payment, invoice, charges
- product_issue: bugs, errors, not working
- delivery: shipping, tracking issues
- refund: refund or return requests
- feedback: suggestions or reviews
- spam: irrelevant or promotional
- general: other cases

Return valid structured output only.
"""),
    ("human", "Subject: {subject}\n\nEmail: {body}")
])


# -----------------------------
# LLM INITIALIZATION
# -----------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=settings.OPENAI_API_KEY,
)


# -----------------------------
# CLASSIFIER FUNCTION
# -----------------------------
async def classify_email(subject: str, body: str) -> ClassificationResult:
    """
    Returns structured classification result for an email.
    """

    structured_llm = llm.with_structured_output(ClassificationResult)

    chain = CLASSIFY_PROMPT | structured_llm

    result = await chain.ainvoke({
        "subject": subject,
        "body": body
    })

    return result