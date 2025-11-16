# main.py (FIXED)
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

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# === CONFIG ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_URL = os.getenv("REPO_URL", "https://github.com/souravkarma/your-portfolio-repo.git")

# FIXED: Use writable directory
BLOGS_DIR = "/opt/render/project/src/blogs"   # This works!
os.makedirs(BLOGS_DIR, exist_ok=True)

# X/Twitter
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

app = FastAPI()
app.mount("/blogs", StaticFiles(directory=BLOGS_DIR), name="blogs")
templates = Jinja2Templates(directory="/opt/render/project/src/templates")  # Also fix

# LLM
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant", temperature=0.8)

TOPICS = [ ... ]  # Your topics list

# X Client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

def post_to_x(text: str):
    try:
        if len(text) > 280:
            text = text[:277] + "..."
        response = client.create_tweet(text=text)
        print(f"Tweeted: {response.data['id']}")
        return True
    except Exception as e:
        print(f"X error: {e}")
        return False

def generate_blog_content():
    topic = random.choice(TOPICS)
    prompt = PromptTemplate.from_template(
        "# {topic}\n\nWrite a 500-word blog in Markdown..."
    )
    chain = prompt | llm | StrOutputParser()
    return topic, chain.invoke({"topic": topic}).strip()

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
            subprocess.run(cmd, cwd=BLOGS_DIR, check=True, stdout=subprocess.DEVNULL)
        print(f"Pushed: {filename}")
    except Exception as e:
        print(f"Git failed: {e}")

async def auto_generate_blog():
    while True:
        print(f"Generating at {datetime.datetime.now().strftime('%H:%M:%S')}")
        topic, content = generate_blog_content()
        save_and_push_blog(topic, content)
        teaser = f"New Blog: {topic}\n{content.split('\n\n')[1][:120]}...\nhttps://souravkarma.github.io/your-portfolio-repo/blogs/\n#AI"
        post_to_x(teaser)
        await asyncio.sleep(60)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.get_template("index.html").render({"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def manual_generate(request: Request, topic: str = Form(...)):
    content = (PromptTemplate.from_template("# {topic}\n\nWrite a 500-word blog...") | llm | StrOutputParser()).invoke({"topic": topic})
    save_and_push_blog(topic, content)
    post_to_x(f"Manual Blog: {topic}\nhttps://souravkarma.github.io/your-portfolio-repo/blogs/\n#AI")
    return templates.get_template("result.html").render({
        "request": request,
        "topic": topic,
        "content": content.replace("\n", "<br>")
    })

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_generate_blog())
