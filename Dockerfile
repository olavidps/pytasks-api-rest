FROM python:3.9-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /app/

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the application
COPY . /app/

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
