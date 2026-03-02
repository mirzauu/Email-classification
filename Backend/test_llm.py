"""
Quick LLM test script - runs outside FastAPI to verify instructor + litellm + openai works.
Usage: .venv/bin/python test_llm.py
"""
import asyncio
import os
import sys

# Load env vars from .env manually
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INFERENCE_MODEL = os.getenv("INFERENCE_MODEL", "openai/gpt-4.1")

print(f"\n{'='*55}")
print(f"  LLM DIAGNOSTIC TEST")
print(f"{'='*55}")
print(f"  Model       : {INFERENCE_MODEL}")
print(f"  API key     : {OPENAI_API_KEY[:20]}..." if OPENAI_API_KEY else "  API key     : ❌ NOT SET")
print(f"{'='*55}\n")

# ── Step 1: Import check ──────────────────────────────────────
print("Step 1: Checking imports...")
try:
    import litellm
    from litellm import acompletion
    import importlib.metadata
    ver = importlib.metadata.version("litellm")
    print(f"  ✅ litellm {ver}")
except ImportError as e:
    print(f"  ❌ litellm not installed: {e}")
    sys.exit(1)

try:
    import instructor
    print(f"  ✅ instructor {instructor.__version__}")
except ImportError as e:
    print(f"  ❌ instructor not installed: {e}")
    sys.exit(1)

# ── Step 2: Basic LLM call via litellm ───────────────────────
print("\nStep 2: Basic litellm acompletion call...")

async def test_basic():
    resp = await acompletion(
        model=INFERENCE_MODEL,
        messages=[{"role": "user", "content": "Say 'hello world' and nothing else."}],
        api_key=OPENAI_API_KEY,
    )
    content = resp.choices[0].message.content
    print(f"  ✅ Response: '{content.strip()}'")
    return content

# ── Step 3: Structured output via instructor ──────────────────
print("\nStep 3: Structured output via instructor.from_litellm...")
from pydantic import BaseModel, Field
from typing import List, Optional

class EmailClassification(BaseModel):
    category: str = Field(description="e.g. finance, travel, work, personal, other")
    summary: str = Field(description="1-2 sentence summary")
    confidence: Optional[float] = Field(default=None, description="0.0-1.0")
    labels: List[str] = Field(default_factory=list, description="keywords")

TEST_EMAIL = """
Subject: Your Amazon Order Has Shipped
Sender: shipment-tracking@amazon.com
Body: Your order #112-3456789-0123456 containing 'Wireless Headphones' has been shipped.
Expected delivery: March 5th. Track your package at amazon.com/orders.
"""

async def test_structured():
    client = instructor.from_litellm(acompletion, mode=instructor.Mode.JSON)
    result = await client.chat.completions.create(
        model=INFERENCE_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an email classifier. Classify the given email accurately."
            },
            {"role": "user", "content": TEST_EMAIL}
        ],
        response_model=EmailClassification,
        api_key=OPENAI_API_KEY,
    )
    print(f"  ✅ category   : {result.category}")
    print(f"  ✅ summary    : {result.summary}")
    print(f"  ✅ confidence : {result.confidence}")
    print(f"  ✅ labels     : {result.labels}")
    return result

async def main():
    try:
        await test_basic()
    except Exception as e:
        print(f"  ❌ Basic call failed: {e}")
        sys.exit(1)

    try:
        await test_structured()
    except Exception as e:
        print(f"  ❌ Structured call failed: {e}")
        sys.exit(1)

    print(f"\n{'='*55}")
    print("  ✅ ALL TESTS PASSED — LLM is working!")
    print(f"{'='*55}\n")

asyncio.run(main())
