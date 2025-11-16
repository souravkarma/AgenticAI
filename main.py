'''
def main():
    print("Hello from agenticai!")


if __name__ == "__main__":
    main()
'''
# main.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

app = FastAPI()

# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama3-8b-8192")

# Prompt Template
prompt = PromptTemplate.from_template(
    "Write a 500-word engaging blog post about: {topic}. "
    "Use markdown, headings, bullet points, and a friendly tone."
)

chain = LLMChain(llm=llm, prompt=prompt)

class BlogRequest(BaseModel):
    topic: str

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>AI Blog Generator</h2>
    <form action="/generate" method="post">
        <input type="text" name="topic" placeholder="Enter blog topic" required style="width:300px;padding:10px;font-size:16px;">
        <button type="submit" style="padding:10px 20px;font-size:16px;">Generate Blog</button>
    </form>
    """

@app.post("/generate")
async def generate_blog(topic: str = Form(...)):
    try:
        result = chain.invoke({"topic": topic})
        blog_content = result['text']
        return f"""
        <h2>Generated Blog</h2>
        <div style="border:1px solid #ccc; padding:20px; border-radius:10px; background:#f9f9f9;">
            {blog_content.replace(chr(10), '<br>')}
        </div>
        <br><a href="/">← Generate Another</a>
        """
    except Exception as e:
        return f"<h3>Error:</h3> <p>{str(e)}</p> <a href='/'>← Back</a>"