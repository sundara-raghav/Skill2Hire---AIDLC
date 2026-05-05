FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY ml-pipeline/requirements.txt ml-pipeline/requirements.txt
COPY backend/requirements.txt backend/requirements.txt

RUN pip install --no-cache-dir -r ml-pipeline/requirements.txt \
 && pip install --no-cache-dir -r backend/requirements.txt

# Copy source
COPY ml-pipeline/ ml-pipeline/
COPY backend/ backend/

# Create runtime directories
RUN mkdir -p ml-pipeline/logs ml-pipeline/reports ml-pipeline/data ml-pipeline/models/trained

EXPOSE 5000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "backend.wsgi:app"]
