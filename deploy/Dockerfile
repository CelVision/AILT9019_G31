FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/server
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 game
COPY server/app ./app
COPY client /app/client
USER game
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import json, urllib.request; r = urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3); assert json.load(r)['status'] == 'healthy'"

# Rooms and queues are process-local; multiple workers cannot share matches.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
