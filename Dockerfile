FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy app files
COPY . .

# Make the script executable
RUN chmod +x start.sh

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose default port (Railway will override this)
EXPOSE 8000

# 🟢 Important: Run using shell so $PORT works at runtime
CMD ["sh", "./start.sh"]
