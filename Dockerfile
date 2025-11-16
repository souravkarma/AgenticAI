FROM python:3.12-slim

WORKDIR /opt/render/project/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create folders in writable location
RUN mkdir -p blogs templates

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
