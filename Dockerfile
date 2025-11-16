# ---- Dockerfile ----
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only what we need (faster layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Create folders that will be used at runtime
RUN mkdir -p templates blogs

# Expose the port (Render will override with $PORT)
EXPOSE 10000

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
