import tweepy
import os
from dotenv import load_dotenv
import time  # For scheduling

# Load env vars
load_dotenv()

# Credentials (from .env)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# Authenticate (X API v2)
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True  # Auto-handles rate limits
)

def post_tweet(text):
    """Post a single tweet (up to 280 chars)."""
    try:
        response = client.create_tweet(text=text)
        print(f"✅ Tweet posted! ID: {response.data['id']} | Text: {text[:50]}...")
        return response.data['id']
    except tweepy.Forbidden as e:
        print(f"❌ Forbidden (403): Check app permissions (Read+Write). Error: {e}")
    except tweepy.NotFound as e:
        print(f"❌ Not Found (404): Invalid tokens. Regenerate Access Tokens. Error: {e}")
    except Exception as e:
        print(f"❌ Error posting: {e}")
        return None

# Example: Post a test tweet
if __name__ == "__main__":
    tweet_text = "Hello from my auto-tweeting bot! 🚀 Built with Python & Tweepy. #AI #DataScience"
    post_tweet(tweet_text)
