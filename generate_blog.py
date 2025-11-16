# generate_blog.py
import os
import subprocess
import datetime
import requests
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# === CONFIG ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
REPO_PATH = "/app/blogs"  # Render mounts repo here
os.makedirs(REPO_PATH, exist_ok=True)

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.8
)

# === RANDOM TOPICS (AI + Data Science) ===
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

# === GENERATE BLOG ===
def generate_blog():
    topic = TOPICS[datetime.datetime.now().second % len(TOPICS)]
    prompt = PromptTemplate.from_template(
        "# {topic}\n\nWrite a 500-word engaging, technical blog post in Markdown. "
        "Include code snippets, bullet points, and a call-to-action at the end."
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"topic": topic})
    return topic, result.strip()

# === SAVE + GIT PUSH ===
def save_and_push(topic, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"blog-{timestamp}.md"
    filepath = os.path.join(REPO_PATH, filename)

    with open(filepath, "w") as f:
        f.write(content)

    # Git commands
    cmds = [
        ["git", "config", "user.name", "AutoBlogBot"],
        ["git", "config", "user.email", "bot@souravkarma.com"],
        ["git", "add", filepath],
        ["git", "commit", "-m", f"Add blog: {topic}"],
        ["git", "push"]
    ]
    for cmd in cmds:
        subprocess.run(cmd, check=True, cwd=REPO_PATH)

# === MAIN ===
if __name__ == "__main__":
    topic, blog = generate_blog()
    save_and_push(topic, blog)
    print(f"Generated: {topic}")
