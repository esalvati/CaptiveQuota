FROM python:3.14-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

VOLUME ["/data"]
EXPOSE 8000

ENV LOG_LEVEL=info

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--workers", "1", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "--capture-output"]
