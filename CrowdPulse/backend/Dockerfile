FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask flask-cors vaderSentiment google-api-python-client python-dotenv textblob
EXPOSE 5010
CMD ["python", "crowdpulse_app.py"]
