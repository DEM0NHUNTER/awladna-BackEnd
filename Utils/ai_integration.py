import os
import logging
import httpx
import re
from datetime import date
from typing import Dict, Any, List, Optional
from textblob import TextBlob

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

HF_TOKEN = os.getenv("HF_TOKEN")
# Environment variables
AI_BASE_URL = os.getenv("AI_BASE_URL", "").rstrip("/")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")


def analyze_sentiment(text: str) -> Dict[str, Any]:
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    label = (
        "positive" if polarity > 0.2 else
        "negative" if polarity < -0.2 else
        "neutral"
    )
    return {"polarity": polarity, "label": label}


def extract_actions(text: str) -> List[str]:
    matches = re.findall(r"(?:•|\d+\.)\s*(.*?)(?=\n|$)", text)
    return [m.strip() for m in matches[:3]]


def extract_recommendations_from_text(text: str) -> List[Dict[str, Any]]:
    """Parse AI response text to extract recommendations."""
    pattern = r"Recommendation:\s*(.+)"
    matches = re.findall(pattern, text)
    recs = []
    for m in matches:
        recs.append({
            "title": m[:40] + "..." if len(m) > 43 else m,
            "description": m,
            "priority": "medium",
            "type": "behavior",
            "source": "ai_model",
            "effective_date": date.today()
        })
    return recs


async def _call_custom_api(prompt: str, age: int, name: str, context: str) -> str:
    """Try your own HTTP endpoint first."""
    if not AI_BASE_URL:
        raise RuntimeError("AI_BASE_URL not set")

    url = f"{AI_BASE_URL}/generate"
    payload = {"prompt": prompt, "age": age, "name": name, "context": context}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("text") or data.get("response") or ""
        if not text:
            raise ValueError("Empty text from custom AI endpoint")
        return text.strip()


async def _call_groq(prompt: str, age: int, name: str, context: str) -> str:
    """Fallback to Groq's OpenAI-compatible API."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    messages = [
        {"role": "system", "content": "You are a helpful parenting assistant."},
        {"role": "user", "content": f"Child: {name}, Age: {age}\nContext: {context}\nQuestion: {prompt}"}
    ]

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def get_ai_response(
        user_input: str,
        child_age: int,
        child_name: str,
        context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Try custom endpoint, fallback to Groq if it fails.
    Returns dict with: response, sentiment_score, sentiment, suggested_actions, ai_recommendations.
    """
    prompt = user_input
    ctx = context or ""

    try:
        text = await _call_custom_api(prompt, child_age, child_name, ctx)
        logger.info("AI response from custom endpoint")
    except Exception as custom_err:
        logger.warning("Custom AI call failed, falling back to Groq: %s", custom_err)
        try:
            text = await _call_groq(prompt, child_age, child_name, ctx)
            logger.info("AI response from Groq fallback")
        except Exception as groq_err:
            logger.error("All AI calls failed: %s", groq_err, exc_info=True)
            return {
                "response": "I'm having trouble responding right now. Please try again later.",
                "sentiment_score": 0.0,
                "sentiment": "neutral",
                "suggested_actions": [],
                "ai_recommendations": []
            }

    sentiment = analyze_sentiment(text)
    actions = extract_actions(text)
    ai_recs = extract_recommendations_from_text(text)

    return {
        "response": text,
        "sentiment_score": sentiment["polarity"],
        "sentiment": sentiment["label"],
        "suggested_actions": actions,
        "ai_recommendations": ai_recs
    }
