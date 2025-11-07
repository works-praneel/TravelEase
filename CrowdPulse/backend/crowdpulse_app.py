from flask import Flask, jsonify, abort
from flask_cors import CORS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os, time, random, logging

# ------------------------
# CONFIGURATION
# ------------------------
load_dotenv()
app = Flask(__name__)  # ✅ Fixed: should be __name, not _name
CORS(app)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# --- YOUTUBE API KEY ---
YOUTUBE_API_KEY = "AIzaSyC4FAL-z4kSa-dzPHN52RiN57lYOaUCXpE"

try:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
except Exception as e:
    youtube = None
    logging.error(f"Failed to initialize YouTube client: {e}")

analyzer = SentimentIntensityAnalyzer()

# --- CITY MAP ---
CITY_MAP = {
    "DEL": "Delhi",
    "BOM": "Mumbai",
    "CCU": "Kolkata",
    "MAA": "Chennai",
    "GOI": "Goa",
    "HYD": "Hyderabad",
    "HKT": "Phuket",
    "SUB": "Juanda",
    "NRT": "Narita",
    "HND": "Haneda",
    "DXB": "Dubai",
    "SYD": "Sydney",
    "MEL": "Melbourne",
    "AKL": "Auckland",
    "LHR": "London",
    "NYC": "New York",
    "LAX": "Los Angeles",
    "CDG": "Paris",
    "TOK": "Tokyo"
}

CACHE = {}
TTL = 600  # 10 minutes

# ------------------------
# UTILITY FUNCTIONS
# ------------------------

def get_youtube_comments(city_name: str):
    """Fetch recent comments about a city from YouTube travel vlogs"""
    comments = []
    if not youtube:
        logging.warning("YouTube client not initialized. Skipping video search.")
        return comments
    try:
        req = youtube.search().list(
            q=f"{city_name} travel vlog tourism experience",
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
                maxResults=10,
                textFormat="plainText"
            )
            comm_res = comm_req.execute()
            for c in comm_res.get("items", []):
                text = c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(text)
    except Exception as e:
        logging.warning(f"[YouTube API Error for {city_name}] {e}")
    return comments


def get_social_posts(city_name: str):
    """Mock data for social posts"""
    sentiments = []
    for _ in range(random.randint(5, 15)):
        adj = random.choice(["amazing", "terrible", "okay", "crowded", "beautiful", "disappointing"])
        text = f"Just visited {city_name}, it was {adj}!"
        score = analyzer.polarity_scores(text)["compound"]
        sentiment = "neutral"
        if score >= 0.05:
            sentiment = "positive"
        elif score <= -0.05:
            sentiment = "negative"
        sentiments.append({
            "text": text,
            "source": random.choice(["Twitter", "Reddit"]),
            "sentiment": sentiment
        })
    return sentiments


def get_youtube_videos(city_name: str):
    """Mock data for YouTube videos"""
    videos = []
    for i in range(random.randint(2, 4)):
        videos.append({
            "title": f"My Awesome Trip to {city_name}! (Vlog #{i+1})",
            "url": "https://www.youtube.com",
            "thumbnail": "https://placehold.co/200x120/6c2bd9/white?text=Vlog"
        })
    return videos

# ------------------------
# ROUTES
# ------------------------

@app.route("/")
def home():
    return "<h3>🌍 CrowdPulse API running</h3>", 200

@app.route("/ping")
def ping():
    """Simple health check for ALB"""
    return "pong", 200

@app.route("/api/crowdpulse/health")
def health_check():
    """Health check for ALB"""
    return "OK", 200

@app.route("/api/crowdpulse/<string:city_code>")
def get_city_pulse(city_code):
    now = time.time()
    city_code = city_code.upper()
    cached = CACHE.get(city_code)
    if cached and now - cached["timestamp"] < TTL:
        logging.info(f"Returning cached data for {city_code}")
        return jsonify(cached["data"])

    city_name = CITY_MAP.get(city_code)
    if not city_name:
        abort(404, description="City code not found")

    social_posts = get_social_posts(city_name)
    youtube_videos = get_youtube_videos(city_name)

    data = {
        "city_code": city_code,
        "city_name": city_name,
        "social_media_posts": social_posts,
        "youtube_videos": youtube_videos,
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    CACHE[city_code] = {"data": data, "timestamp": now}
    return jsonify(data)

# ------------------------
# ENTRY POINT
# ------------------------
if __name__ == "__main__":  # ✅ Fixed
    app.run(host="0.0.0.0", port=5010, debug=False)