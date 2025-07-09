# BackEnd/Utils/translation.py
from googletrans import Translator
from fastapi import Request, Response
from typing import Dict, List, Optional

translator = Translator()


def detect_language(text: str) -> str:
    """Detect input language using Google Translate API"""
    try:
        result = translator.detect(text)
        return result.lang if result.lang in ["en", "ar"] else "en"
    except Exception as e:
        logging.warning(f"Language detection failed: {e}")
        return "en"


def translate_text(text: str, target_lang: str) -> str:
    """Translate text using Google Translate API"""
    try:
        return translator.translate(text, src="en", dest=target_lang).text
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text  # Fallback to original
