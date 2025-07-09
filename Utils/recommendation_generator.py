from typing import List, Dict
from datetime import date
from BackEnd.Models.recommendation import RecommendationSource, RecommendationPriority

def generate_recommendations_from_behavior(data: Dict) -> List[Dict]:
    recs = []
    if "tantrums" in data:
        recs.append({
            "title": "Handle Tantrums",
            "description": "Use timeout and positive reinforcement strategies.",
            "priority": RecommendationPriority.HIGH,
            "source": RecommendationSource.AI_MODEL,
            "effective_date": date.today(),
            "type": "behavior",
            "metadata": '{"steps": ["Timeout", "Reward system"]}'
        })
    return recs

def generate_recommendations_from_emotion(data: Dict) -> List[Dict]:
    recs = []
    if data.get("anxiety", 0) > 0.7:
        recs.append({
            "title": "Reduce Anxiety",
            "description": "Create a predictable daily routine and provide reassurance.",
            "priority": RecommendationPriority.HIGH,
            "source": RecommendationSource.AI_MODEL,
            "effective_date": date.today(),
            "type": "emotional",
            "metadata": '{"activities": ["Routine chart", "Reassurance phrases"]}'
        })
    return recs
