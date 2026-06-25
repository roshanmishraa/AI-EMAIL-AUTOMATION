from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings
from app.services.ai.rag import retrieve_relevant_chunks


# -----------------------------
# RESPONSE SCHEMA
# -----------------------------
class ReplyResult(BaseModel):
    draft_reply: str
    confidence_score: float
    escalation_flag: bool
    escalation_reason: Optional[str]
    tone_used: str


# -----------------------------
# TONE SYSTEM (AS PER PROJECT BRIEF)
# -----------------------------
TONE_MAP = {
    "angry": "Empathetic, acknowledge frustration immediately, provide solution.",
    "frustrated": "Calm, patient, step-by-step resolution focused.",
    "neutral": "Professional and concise.",
    "happy": "Friendly and positive brand tone.",
    "sad": "Supportive and reassuring tone.",
    "legal": "Formal, careful, no liability admission, escalate if needed."
}


# -----------------------------
# PROMPT
# -----------------------------
REPLY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI customer support assistant.

Use the provided knowledge base context to generate accurate replies.

Tone:
{tone_instruction}

Knowledge Base Context:
{kb_context}

Rules:
- Be concise (max 200 words)
- Be helpful and solution-focused
- Do NOT hallucinate facts (order IDs, refunds, etc.)
- If unsure, suggest escalation
"""),
    ("human", """
Subject: {subject}
Category: {category}
Sentiment: {sentiment}

Email Body:
{body}
"""),
])


# -----------------------------
# MAIN FUNCTION
# -----------------------------
async def generate_reply(
    subject: str,
    body: str,
    category: str,
    sentiment: str
) -> ReplyResult:

    # -------------------------
    # RAG CONTEXT FETCH
    # -------------------------
    kb_chunks = await retrieve_relevant_chunks(body)

    kb_context = (
        "\n\n".join(kb_chunks)
        if kb_chunks
        else "No relevant knowledge base information found."
    )

    # -------------------------
    # TONE SELECTION LOGIC
    # -------------------------
    tone_key = "legal" if category == "legal" else sentiment
    tone_instruction = TONE_MAP.get(tone_key, TONE_MAP["neutral"])

    # -------------------------
    # LLM
    # -------------------------
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY
    )

    structured_llm = llm.with_structured_output(ReplyResult)

    chain = REPLY_PROMPT | structured_llm

    # -------------------------
    # EXECUTION (SAFE)
    # -------------------------
    try:
        result = await chain.ainvoke({
            "subject": subject,
            "body": body,
            "category": category,
            "sentiment": sentiment,
            "kb_context": kb_context,
            "tone_instruction": tone_instruction
        })

        return result

    except Exception:
        # -------------------------
        # FALLBACK (VERY IMPORTANT FOR DEMO)
        # -------------------------
        return ReplyResult(
            draft_reply=(
                "Thank you for contacting us. "
                "We have received your request and are looking into it. "
                "Our team will respond shortly."
            ),
            confidence_score=50.0,
            escalation_flag=False,
            escalation_reason=None,
            tone_used="fallback"
        )