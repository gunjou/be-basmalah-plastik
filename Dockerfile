FROM python:3.11-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh aplikasi
COPY . .

# Jalankan pakai Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:api"]
