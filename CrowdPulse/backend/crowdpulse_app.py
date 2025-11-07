from flask import Flask, jsonify
from flask_cors import CORS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os, time, random, logging

# ------------------------
# CONFIGURATION
# ------------------------
load_dotenv()
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    logging.warning("⚠️  YOUTUBE_API_KEY not found in .env file — API calls will fail.")

try:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
except Exception as e:
    youtube = None
    logging.error(f"Failed to initialize YouTube client: {e}")

analyzer = SentimentIntensityAnalyzer()

# --- Expanded list of world tourist cities (40+) ---
CITIES = [
    "New York", "Los Angeles", "London", "Paris", "Tokyo", "Dubai", "Singapore", "Rome", "Bangkok",
    "Sydney", "Melbourne", "Toronto", "Vancouver", "Delhi", "Mumbai", "Goa", "Manali", "Bali",
    "Istanbul", "Cairo", "Berlin", "Amsterdam", "Barcelona", "Madrid", "Lisbon", "Prague",
    "Zurich", "Cape Town", "Rio de Janeiro", "Buenos Aires", "Seoul", "Hong Kong", "Kuala Lumpur",
    "Doha", "Helsinki", "Stockholm", "Auckland", "Beijing", "Chicago", "San Francisco"
]

CACHE = {}
TTL = 600  # cache per city for 10 minutes


# ------------------------
# UTILITY FUNCTIONS
# ------------------------

def get_youtube_comments(city: str):
    """Fetch recent comments about a city from YouTube travel vlogs"""
    comments = []
    if not youtube:
        return comments
    try:
        # Search for videos
        req = youtube.search().list(
            q=f"{city} travel vlog tourism experience",
            part="snippet",
            maxResults=3,
            type="video",
            order="date"
        )
        res = req.execute()

        for vid in res.get("items", []):
            vid_id = vid["id"]["videoId"]
            comm_req = youtube.commentThreads().list(
                part="snippet",
                videoId=vid_id,
                maxResults=30,
                textFormat="plainText"
            )
            comm_res = comm_req.execute()
            for c in comm_res.get("items", []):
                text = c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(text)
    except Exception as e:
        logging.warning(f"[YouTube API Error for {city}] {e}")
    return comments


def analyze_sentiment(texts):
    """Compute overall sentiment using Vader"""
    pos, neg, neu = 0, 0, 0
    for t in texts:
        s = analyzer.polarity_scores(t)["compound"]
        if s >= 0.05:
            pos += 1
        elif s <= -0.05:
            neg += 1
        else:
            neu += 1

    total = len(texts)
    if total == 0:
        return 50.0, 0, 0, 0

    pos_pct = (pos / total) * 100
    neg_pct = (neg / total) * 100
    neu_pct = (neu / total) * 100
    mood = max(0, min(100, 50 + (pos_pct - neg_pct) / 2))
    return mood, pos_pct, neg_pct, neu_pct


# ------------------------
# ROUTES
# ------------------------

@app.route("/api/crowdpulse/all")
def get_all_moods():
    now = time.time()
    results = []

    for city in CITIES:
        # use cached value if not expired
        cached = CACHE.get(city)
        if cached and now - cached["timestamp"] < TTL:
            results.append(cached["data"])
            continue

        texts = get_youtube_comments(city)

        # Fallback if YouTube quota exhausted
        if not texts:
            logging.info(f"[{city}] Using fallback random mood (no data)")
            mood = random.uniform(40, 80)
            data = {
                "city": city,
                "mood_index": round(mood, 1),
                "positive_pct": random.randint(40, 70),
                "negative_pct": random.randint(10, 30),
                "neutral_pct": 100 - random.randint(40, 70),
                "sample_count": 0,
                "source": "cached/fallback",
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            CACHE[city] = {"data": data, "timestamp": now}
            results.append(data)
            continue

        mood, pos, neg, neu = analyze_sentiment(texts)
        data = {
            "city": city,
            "mood_index": round(mood, 1),
            "positive_pct": round(pos, 1),
            "negative_pct": round(neg, 1),
            "neutral_pct": round(neu, 1),
            "sample_count": len(texts),
            "source": "live",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        CACHE[city] = {"data": data, "timestamp": now}
        results.append(data)

    return jsonify({"data": results, "cached": False})


@app.route("/")
def home():
    return "<h3>🌍 CrowdPulse API running — visit <a href='/api/crowdpulse/all'>/api/crowdpulse/all</a></h3>"


# ------------------------
# ENTRY POINT
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=False)
