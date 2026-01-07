FROM python:3.12-slim

WORKDIR /app

# If you later need system deps for compiled wheels, add them here.

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Streamlit config: listen on all interfaces, default port 8501
EXPOSE 8501

# Run the dashboard
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
