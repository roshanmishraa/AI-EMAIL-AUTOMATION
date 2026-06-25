import pytest
from app.services.ai.rag import add_document_to_index, retrieve_relevant_chunks

SAMPLE_KB = """
Our return policy allows returns within 30 days of delivery.
Items must be unused and in original packaging.
To initiate a return, contact support@company.com with your order ID.
Refunds are processed within 5-7 business days.
"""

@pytest.mark.asyncio
async def test_add_and_retrieve():
    count = await add_document_to_index(SAMPLE_KB, source="return_policy")
    assert count > 0
    results = await retrieve_relevant_chunks("how do I return my order")
    assert len(results) > 0
    assert any("return" in r.lower() for r in results)
