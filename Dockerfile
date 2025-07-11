# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app/mcp

# Copy the requirements file into the container at /app/mcp
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# The `aula 4/mcp` directory will be copied into `/app/mcp`
COPY . .

# Set environment variables for API keys (replace with your actual env vars if different)
# It's recommended to pass these at runtime using -e or a .env file with docker-compose
ENV GOOGLE_API_KEY=""
ENV OPENAI_API_KEY=""
ENV ANTHROPIC_API_KEY=""

# Command to run the application
# This will execute the example usage in orchestration_engine.py
CMD ["python", "core/orchestration_engine.py"]