from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings
from app.services.ai.rag import retrieve_relevant_chunks


# ──────────────────────────────────────────
# RESPONSE SCHEMA
# ──────────────────────────────────────────
class ReplyResult(BaseModel):
    draft_reply:       str
    confidence_score:  float          # 0–100
    escalation_flag:   bool
    escalation_reason: Optional[str]
    tone_used:         str


# ──────────────────────────────────────────
# TONE MAP (matches brief exactly)
# ──────────────────────────────────────────
TONE_MAP = {
    "angry":      "Empathetic, acknowledge frustration immediately, solution-first.",
    "frustrated": "Calm, patient, step-by-step resolution focused.",
    "neutral":    "Professional and concise.",
    "happy":      "Friendly and positive brand-forward tone.",
    "sad":        "Warm, human, supportive and reassuring.",
    "legal":      "Formal, careful, no liability admission, recommend escalation.",
}


# ──────────────────────────────────────────
# PROMPT
# ──────────────────────────────────────────
REPLY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are an AI customer support assistant for BeastLife, an Indian sports nutrition brand.

Use the knowledge base context below to generate accurate, grounded replies.

Tone instruction:
{tone_instruction}

Knowledge Base Context:
{kb_context}

Rules:
- Be concise (max 200 words)
- Be helpful and solution-focused
- Do NOT fabricate order IDs, dates, amounts, or policies not in KB
- confidence_score MUST be between 0 and 100 (not 0 to 1)
- If KB context is relevant and answers the query: confidence_score = 85-95, escalation_flag = false
- If KB context is missing or irrelevant: confidence_score = 40, escalation_flag = false
- ONLY set escalation_flag = true if category is 'legal'
- Never set escalation_flag = true just because you are unsure
"""),
    ("human", """\
Subject: {subject}
Category: {category}
Sentiment: {sentiment}

Email Body:
{body}
"""),
])


# ──────────────────────────────────────────
# MAIN FUNCTION
# ──────────────────────────────────────────
async def generate_reply(
    subject:   str,
    body:      str,
    category:  str,
    sentiment: str,
) -> ReplyResult:

    # ── 1. Category-filtered RAG retrieval (KEY FIX) ──
    kb_chunks = await retrieve_relevant_chunks(
        query=body,
        category=category,   # only pull chunks tagged for this category
    )
    kb_context = (
        "\n\n---\n\n".join(kb_chunks)
        if kb_chunks
        else "No relevant knowledge base articles found for this category."
    )

    # ── 2. Tone selection ──
    tone_key         = "legal" if category == "legal" else sentiment
    tone_instruction = TONE_MAP.get(tone_key, TONE_MAP["neutral"])

    # ── 3. LLM ──
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY,
    )
    structured_llm = llm.with_structured_output(ReplyResult)
    chain          = REPLY_PROMPT | structured_llm

    # ── 4. Execute with safe fallback ──
    try:
        result = await chain.ainvoke({
            "subject":          subject,
            "body":             body,
            "category":         category,
            "sentiment":        sentiment,
            "kb_context":       kb_context,
            "tone_instruction": tone_instruction,
        })
        return result

    except Exception as e:
        print(f"[ReplyGenerator] LLM error: {e}")
        return ReplyResult(
            draft_reply=(
                "Thank you for reaching out. We have received your message and "
                "our team will review it shortly. We apologise for any inconvenience."
            ),
            confidence_score=40.0,
            escalation_flag=True,       # low confidence → auto escalate
            escalation_reason="llm_error",
            tone_used="fallback",
        )