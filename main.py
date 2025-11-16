# main.py
import os
import subprocess
import datetime
import random
import asyncio
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import tweepy
from dotenv import load_dotenv

# LangChain imports (new syntax)
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# === CONFIG ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_URL = os.getenv("REPO_URL", "https://github.com/souravkarma/your-portfolio-repo.git")
BLOGS_DIR = "/app/blogs"
os.makedirs(BLOGS_DIR, exist_ok=True)

# X/Twitter Credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Initialize FastAPI
app = FastAPI(title="Auto Blog + X Poster")
app.mount("/blogs", StaticFiles(directory=BLOGS_DIR), name="blogs")
templates = Jinja2Templates(directory="/app/templates")

# === LLM SETUP ===
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.8
)

# === TOPICS (AI + Data Science) ===
TOPICS = [
    "How LangChain is Revolutionizing AI Agents in 2025",
    "Top 5 Data Science Tools Every Analyst Must Know",
    "Building Real-Time Stock Prediction with Python and Groq",
    "Why Llama 3.1 is Beating GPT-4 in Speed and Cost",
    "MLOps in 2025: From Prototype to Production in 5 Minutes",
    "The Rise of Agentic AI: What It Means for Developers",
    "How to Fine-Tune LLMs on Your Laptop (No GPU Needed)",
    "Data Privacy in AI: GDPR, CCPA, and Beyond",
    "Vector Databases: The Future of Semantic Search",
    "AutoML in 2025: When Machines Build Better Models Than Humans"
]

# === X/TWITTER CLIENT ===
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

def post_to_x(text: str):
    """Post tweet and return success status."""
    try:
        if len(text) > 280:
            text = text[:277] + "..."
        response = client.create_tweet(text=text)
        print(f"Posted to X: {response.data['id']}")
        return True
    except Exception as e:
        print(f"X Post Failed: {e}")
        return False

# === BLOG GENERATOR ===
def generate_blog_content():
    topic = random.choice(TOPICS)
    prompt = PromptTemplate.from_template(
        "# {topic}\n\n"
        "Write a 500-word technical blog post in Markdown.\n"
        "Include:\n"
        "- Catchy intro\n"
        "- 3–4 key points with bullet points\n"
        "- Code snippet (Python)\n"
        "- Conclusion with CTA\n"
        "- Use ## for subheadings\n"
        "- Friendly, expert tone"
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"topic": topic})
    return topic, result.strip()

# === SAVE + GIT PUSH ===
def save_and_push_blog(topic: str, content: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"blog-{timestamp}.md"
    filepath = os.path.join(BLOGS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Git push
    try:
        cmds = [
            ["git", "config", "user.name", "AutoBlogBot"],
            ["git", "config", "user.email", "bot@souravkarma.com"],
            ["git", "add", filepath],
            ["git", "commit", "-m", f"Add blog: {topic}"],
            ["git", "push", f"https://{GITHUB_TOKEN}@github.com/souravkarma/your-portfolio-repo.git", "HEAD:main"]
        ]
        for cmd in cmds:
            subprocess.run(cmd, cwd=BLOGS_DIR, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Blog saved & pushed: {filename}")
    except Exception as e:
        print(f"Git push failed: {e}")

# === AUTO BLOG TASK (Runs every 60 seconds) ===
async def auto_generate_blog():
    while True:
        print(f"Generating blog at {datetime.datetime.now().strftime('%H:%M:%S')}")
        topic, content = generate_blog_content()

        # Save + push
        save_and_push_blog(topic, content)

        # Tweet teaser
        teaser = f"New Blog: {topic}\n\n{content.split('\n\n')[1][:120]}...\n\nRead more: https://souravkarma.github.io/your-portfolio-repo/blogs/\n#AI #DataScience #Python"
        post_to_x(teaser)

        await asyncio.sleep(60)  # Every 1 minute

# === WEB UI ===
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.get_template("index.html").render({"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def manual_generate(request: Request, topic: str = Form(...)):
    prompt = PromptTemplate.from_template(
        "# {topic}\n\nWrite a 500-word engaging blog post in Markdown..."
    )
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"topic": topic})

    # Save manually too
    save_and_push_blog(topic, content)
    post_to_x(f"Manual Blog: {topic}\nRead: https://souravkarma.github.io/your-portfolio-repo/blogs/\n#AI")

    return templates.get_template("result.html").render({
        "request": request,
        "topic": topic,
        "content": content.replace("\n", "<br>")
    })

# === START AUTO TASK ON STARTUP ===
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_generate_blog())
