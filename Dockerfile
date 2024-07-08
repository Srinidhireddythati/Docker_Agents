# Use a specific Python version with a multi-stage build for efficiency
FROM python:3.8-slim AS builder

# Set working directory for building dependencies
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies only in the builder stage
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Use a smaller runtime image without unnecessary build tools
FROM python:3.8-slim

# Set working directory in the runtime container
WORKDIR /app

# Copy application code from the builder stage
COPY --from=builder /app /app

# Install openai module
RUN pip install openai==0.28

# Expose port 8501 (adjust if your script uses a different port)
EXPOSE 8501

# Define the default CSV file path as an environment variable
ENV CSV_FILE=/app/sample_dataset.csv

# Command to run your Python script
CMD ["python", "main.py", "--csv", "/app/sample_dataset.csv"]


#This app is created inside the docker(image/container) to keep track of all lib and codes