# AgenticAI – AI Blog Generator

An **Agentic AI** system using **LangChain + Groq + Llama3** to generate full SEO-optimized blog posts from a single prompt.

## Features
- Generate 500+ word blog posts in seconds
- Markdown formatting with headings, lists, code blocks
- Deployed as a **live API** on Render
- Integrated into [souravkarma.github.io](https://souravkarma.github.io) portfolio

## Live Demo
Click **"Generate AI Blog"** on my [portfolio](https://souravkarma.github.io) → type any topic → get a full blog!

## Tech Stack
- **LangChain** – Agentic workflow
- **Groq + Llama3** – Ultra-fast inference
- **FastAPI** – Backend API
- **Render.com** – Free hosting

## Setup
```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key
uvicorn main:app --reload
