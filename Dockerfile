# Use the official Python image as a base image
FROM python:3.12

# Set environment variables for Poetry
ENV POETRY_HOME=/etc/poetry
ENV POETRY_VERSION=1.3.2
ENV PATH=$POETRY_HOME/bin:$PATH

# Set the working directory
WORKDIR /app

# Install necessary system packages and Poetry
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk python3-distutils unzip curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION && \
    chmod +x $POETRY_HOME/bin/poetry && \
    poetry config virtualenvs.create false

# Verify distutils installation
RUN python3 -m ensurepip --upgrade && \
    python3 -m pip install --upgrade pip setuptools wheel

# Install required packages and download Liquibase
RUN curl -o /app/liquibase.zip -L "https://github.com/liquibase/liquibase/releases/download/v4.29.1/liquibase-4.29.1.zip" && \
    unzip /app/liquibase.zip -d /usr/local/liquibase/ && \
    rm /app/liquibase.zip && \
    curl -o /usr/local/liquibase/lib/liquibase-neo4j-4.29.1-full.jar -L "https://github.com/liquibase/liquibase-neo4j/releases/download/v4.29.1/liquibase-neo4j-4.29.1-full.jar" && \
    ln -s /usr/local/liquibase/liquibase /usr/local/bin/liquibase && \
    chmod +x /usr/local/bin/liquibase

# Copy only pyproject.toml and poetry.lock to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

# Install dependencies using Poetry
RUN poetry install --with dev

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