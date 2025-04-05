# Start from a Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your requirements first (helps with caching)
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Copy your project files
COPY . .

# Expose the port your app runs on (optional but good practice)
EXPOSE 8000

# Start your app (update to your actual entrypoint)
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
