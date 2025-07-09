# BackEnd/demo/demo_recommendations_flow.py
from datetime import date
from BackEnd.Utils.database import get_mongo_collection_custom
from BackEnd.Schemas.child_profile import (
    BehaviorRecommendation,
    RecommendationSource,
    RecommendationPriority,
)


def demo_recommendations_flow():
    """
    Demonstrates creating behavior recommendations,
    printing them, and storing them in MongoDB.
    """

    # Create a list of behavior recommendations with various details
    recs = [
        BehaviorRecommendation(
            title="Bedtime Routine",
            description="Establish a consistent routine before bed.",
            source=RecommendationSource.AI_MODEL,  # Source enum (AI generated)
            priority=RecommendationPriority.HIGH,  # Priority enum (High)
            effective_date=date.today(),  # Today's date
            behavior_target="bedtime",
            expected_outcome="child falls asleep easily",
            steps=["Dim lights...", "Read a story", "Say goodnight"],
            scientific_basis="Numerous pediatric studies",
        ),
        BehaviorRecommendation(
            title="Praise Good Behavior",
            description="Use positive reinforcement.",
            source=RecommendationSource.EDUCATOR,  # Source enum (Educator)
            priority=RecommendationPriority.MEDIUM,  # Priority enum (Medium)
            effective_date=date.today(),
            behavior_target="general",
            expected_outcome="increase in desired behaviors",
            steps=[
                "Catch them being good",
                "Use specific praise",
                "Offer small rewards",
            ],
            scientific_basis="Operant conditioning research",
        ),
    ]

    # Print a simple summary of generated recommendations
    print("\n📝 Generated Recommendations:")
    for r in recs:
        print(f"- {r.title} ({r.priority.value})")

    # Manually serialize enums and dates before inserting into MongoDB
    docs = []
    for r in recs:
        doc = {
            "title": r.title,
            "description": r.description,
            "source": r.source.value,  # Convert enum to string value
            "priority": r.priority.value,  # Convert enum to string value
            "effective_date": r.effective_date.isoformat(),  # Serialize date to ISO string
            "expiration_date": (r.expiration_date.isoformat() if r.expiration_date else None),  # Optional date
            "behavior_target": r.behavior_target,
            "expected_outcome": r.expected_outcome,
            "steps": r.steps,
            "scientific_basis": r.scientific_basis,
        }
        docs.append(doc)

    # Get MongoDB collection handle
    col = get_mongo_collection_custom("recommendations")
    # Insert all recommendation documents into MongoDB
    result = col.insert_many(docs)
    print(f"\n✅ Inserted {len(result.inserted_ids)} recommendations into MongoDB")


# Run the demo if this script is executed directly
if __name__ == "__main__":
    demo_recommendations_flow()
