from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Literal
from app.core.config import settings


class ClassificationResult(BaseModel):
    category: Literal[
        "legal", "billing", "product_issue",
        "delivery", "refund", "general", "spam", "feedback"
    ]
    confidence: float  # 0-100
    reasoning: str


CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are an expert customer support email classifier for BeastLife, an Indian sports nutrition brand.

Classify the email into ONE category:

- legal: lawsuits, GDPR, legal threats, attorney mentions
- billing: payment issues, invoice, overcharge, wrong amount charged
- product_issue: lumps in protein, bad taste, quality complaints, side effects
- delivery: shipping, tracking, not received, wrong address
- refund: refund or return requests
- feedback: suggestions, reviews, compliments
- spam: irrelevant, promotional, newsletters, personal messages, HTML-heavy marketing emails unrelated to BeastLife customer support
- general: product info questions, how-to, other customer queries

IMPORTANT RULES:
- confidence MUST be between 0 and 100 (not 0 to 1)
- 95 = very confident, 75 = confident, 50 = unsure
- Personal messages, friend chats, non-customer emails = spam with confidence 95
- BeastLife customer support emails = appropriate category with confidence 85-95

SPAM DETECTION — classify as spam with confidence 95 if ANY of these are true:
  * Email body contains large amounts of HTML/CSS/JavaScript markup (newsletters, Substack, marketing)
  * Email is a newsletter or promotional broadcast (not a direct customer query)
  * Email sender is a no-reply address (noreply@, donotreply@, newsletter@)
  * Email has no direct question or complaint about BeastLife products/orders
  * Email is a job alert, subscription digest, or automated notification

Return valid structured output only.
"""),
    ("human", "Subject: {subject}\n\nEmail: {body}")
])


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=settings.OPENAI_API_KEY,
)


async def classify_email(subject: str, body: str) -> ClassificationResult:

    # ── PRE-CHECK: HTML-heavy body → mark as spam immediately ──
    # Saves LLM tokens for obvious newsletters/Substack emails
    html_indicators = ['<html', '<head>', '<style>', '<!doctype', '@media', 'font-family:']
    body_lower = (body or '').lower()
    html_count = sum(1 for tag in html_indicators if tag in body_lower)

    if html_count >= 3:
        # Body is clearly an HTML email — classify as spam without calling LLM
        print(f"[Classifier] HTML-heavy body detected ({html_count} indicators) → spam (no LLM call)")
        return ClassificationResult(
            category="spam",
            confidence=95.0,
            reasoning="Email body contains heavy HTML/CSS markup — classified as newsletter or promotional email"
        )

    structured_llm = llm.with_structured_output(ClassificationResult)
    chain = CLASSIFY_PROMPT | structured_llm
    result = await chain.ainvoke({
        "subject": subject,
        "body": body
    })
    return result