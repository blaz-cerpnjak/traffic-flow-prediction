# Use an official Python runtime as a parent image
FROM python:3.11-slim

ENV PATH="${PATH}:/root/.poetry/bin"
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Set the working directory
WORKDIR /app

# Install dependencies
RUN pip install pandas requests uvicorn fastapi onnxruntime python-dotenv pymongo mlflow onnx

# Copy the rest of the application code
COPY ./src /app/src
COPY ./src/utils /app/src/utils
COPY ./data /app/data
# COPY .env /app/.env

# Create a README file
RUN echo "Welcome to my Docker image!" > /app/README.md

# Expose the application port
EXPOSE 8000

WORKDIR /app/src/serve

# Command to run the application
#CMD ["uvicorn", "src.serve.api:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["python", "-m", "src.serve.api"]
CMD ["python", "api.py"]