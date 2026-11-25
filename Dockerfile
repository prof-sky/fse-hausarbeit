# Bau:   docker build -t mensch .
# Start: docker run --rm -p 8080:8080 -e OPENROUTER_API_KEY mensch
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# nur benötigte Dateien kopieren; COPY . . würde auch eine lokale .env ins Image nehmen
COPY app.py persona.md index.html ./

# 0.0.0.0, sonst ist der Dienst von außerhalb des Containers nicht erreichbar
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
