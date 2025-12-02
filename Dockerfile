FROM python:3.12-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App rein kopieren
COPY . .

# Flask starten
CMD ["python", "app.py"]
