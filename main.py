'''
def main():
    print("Hello from agenticai!")


if __name__ == "__main__":
    main()
'''
# main.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()

# === CONFIG ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in environment variables!")

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",
    temperature=0.7
)

# === PROMPT + CHAIN (NEW LANGCHAIN SYNTAX) ===
prompt = PromptTemplate.from_template(
    "Write a 500-word engaging blog post in markdown about: {topic}\n\n"
    "Include:\n"
    "- A catchy title\n"
    "- Introduction\n"
    "- 3–4 key points with bullet points\n"
    "- Conclusion\n"
    "- Friendly, professional tone"
)

chain = prompt | llm | StrOutputParser()

# === ROUTES ===
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <div style="font-family: Arial; max-width: 600px; margin: 40px auto; padding: 20px; text-align: center;">
        <h2 style="color: #002D62;">AI Blog Generator</h2>
        <p style="color: #555; margin: 15px 0;">Enter any topic and get a full blog post instantly!</p>
        <form action="/generate" method="post" style="margin: 25px 0;">
            <input type="text" name="topic" placeholder="e.g., Future of AI in Stock Trading" 
                   required style="width: 70%; padding: 12px; font-size: 16px; border: 1px solid #002D62; border-radius: 8px;">
            <button type="submit" style="padding: 12px 24px; font-size: 16px; background: #002D62; color: white; border: none; border-radius: 8px; cursor: pointer; margin-left: 10px;">
                Generate Blog
            </button>
        </form>
        <p style="font-size: 0.9em; color: #888;">Powered by Groq + LangChain</p>
    </div>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_blog(topic: str = Form(...)):
    try:
        print(f"Generating blog for: {topic}")
        result = chain.invoke({"topic": topic})
        blog_content = result.strip()

        # Convert newlines to <br> for HTML
        formatted = blog_content.replace("\n", "<br>")

        return f"""
        <div style="font-family: Arial; max-width: 700px; margin: 40px auto; padding: 20px; background: #f9f9f9; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h2 style="color: #002D62; text-align: center;">Generated Blog</h2>
            <div style="background: white; padding: 25px; border-radius: 10px; border: 1px solid #eee; line-height: 1.7; text-align: left;">
                {formatted}
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/" style="color: #002D62; font-weight: bold;">← Generate Another</a>
            </div>
        </div>
        """
    except Exception as e:
        return f"""
        <div style="text-align: center; padding: 40px; color: red;">
            <h3>Error Generating Blog</h3>
            <p>{str(e)}</p>
            <a href="/">← Try Again</a>
        </div>
        """
