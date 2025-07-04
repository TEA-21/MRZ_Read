FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

# ✅ Corrected CMD (uses shell for variable expansion)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port=${PORT:-8000}"
