# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose port (match your Flask API port)
EXPOSE 5001

# Run the app
CMD ["python", "main.py"]
