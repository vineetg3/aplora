# Use Python 3.10 or higher base image
FROM python:3.10-slim

# Rest of the Dockerfile remains the same
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001
ENV OPENAI_API_KEY=your_api_key_here
EXPOSE 5001
CMD ["flask", "run", "--port", "5001"]