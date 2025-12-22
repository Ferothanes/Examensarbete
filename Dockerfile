FROM python:3.12-slim

WORKDIR /app

# Install system deps (if any compiled wheels are needed later, add build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Streamlit config: listen on all interfaces, default port 8501
EXPOSE 8501

# Run the dashboard
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
