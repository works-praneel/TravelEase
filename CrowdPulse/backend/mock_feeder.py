# backend/mock_feeder.py
import os
import json
import random
import time

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CITIES = [
    "Goa", "Manali", "Delhi", "Mumbai", "Paris", "New York", "Tokyo",
    "London", "Dubai", "Sydney", "Singapore", "Bangkok", "Berlin",
    "Bali", "Rome", "Cape Town", "Istanbul", "Toronto", "Hong Kong", "Barcelona"
]

MOODS = [
    "positive", "positive", "positive", "neutral", "negative"
]

EXAMPLES = {
    "positive": [
        "Beautiful weather and amazing vibes!",
        "Loved the food and people here!",
        "Great nightlife and stunning places to visit!",
        "Had a relaxing time, can’t wait to come back!"
    ],
    "neutral": [
        "Trip was okay, not much to say.",
        "It’s fine, just like any other place.",
        "Mixed feelings, some things good and some not."
    ],
    "negative": [
        "Too crowded and expensive!",
        "Bad service and heavy traffic.",
        "Not worth the hype, disappointed."
    ]
}
def generate_mock_posts(city):
    posts = []
    # Randomly bias sentiment by region for realism
    bias = random.choice(["positive", "neutral", "negative"])
    for _ in range(random.randint(40, 100)):
        mood = random.choices(
            ["positive", "negative", "neutral"],
            weights={
                "positive": [0.6, 0.2, 0.3][["positive","neutral","negative"].index(bias)],
                "negative": [0.2, 0.3, 0.5][["positive","neutral","negative"].index(bias)],
                "neutral":  [0.2, 0.5, 0.2][["positive","neutral","negative"].index(bias)]
            }[["positive","neutral","negative"].index(bias)],
            k=1
        )[0]
        posts.append({
            "text": random.choice(EXAMPLES[mood]),
            "sentiment": mood
        })
    with open(os.path.join(DATA_DIR, f"{city.lower()}_posts.json"), "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)


if __name__ == "__main__":
    print("Generating mock sentiment data...")
    while True:
        for city in CITIES:
            generate_mock_posts(city)
        print("Cycle complete. Updating again in 2 minutes...")
        time.sleep(120)
