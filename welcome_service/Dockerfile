FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list and install it
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and template
COPY app.py .
COPY template.docx .

# Expose the service port
EXPOSE 5001

# Start the Flask service
CMD ["python", "app.py"]
