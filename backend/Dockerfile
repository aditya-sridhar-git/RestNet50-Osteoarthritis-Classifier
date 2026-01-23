# Production Backend-only Dockerfile
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

# Copy all backend code (which now includes frontend/dist)
COPY . .

# Ensure frontend/dist exists in the container
# Our local move command put it in backend/frontend/dist, 
# and WORKDIR is /app, and we COPY . ., so it will be at /app/frontend/dist

# Expose port
ENV PORT=5000
EXPOSE 5000

# Run the app using gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app
