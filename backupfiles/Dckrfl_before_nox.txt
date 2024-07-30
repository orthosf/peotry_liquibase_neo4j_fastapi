# Use the official Python image as a base image
FROM python:3.12

# Set the working directory
WORKDIR /app

ENV POETRY_HOME /etc/poetry
ENV POETRY_VERSION 1.3.2
ENV PATH $POETRY_HOME/bin:$PATH

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION && \
    chmod +x $POETRY_HOME/bin/poetry && \
    poetry config virtualenvs.create false

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy only pyproject.toml and poetry.lock to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

# Install dependencies using Poetry
RUN poetry install 

# Copy the entire application code to the working directory
COPY ./src /app/src

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONPATH="/app"

# Set the working directory to /app/src
WORKDIR /app/src

# Set the command to run your application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]