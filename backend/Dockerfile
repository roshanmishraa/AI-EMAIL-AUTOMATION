$content = @'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
'@
Set-Content -Path "D:\ai-email-automation\ai-email-automation\backend\Dockerfile" -Value $content