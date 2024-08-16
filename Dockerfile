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

# Install Java (required for Liquibase)
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install required packages and download Liquibase
RUN curl -o /app/liquibase.zip -L "https://github.com/liquibase/liquibase/releases/download/v4.16.0/liquibase-4.16.0.zip" && \
    apt-get update && \
    apt-get install -y unzip && \
    unzip /app/liquibase.zip -d /usr/local/liquibase/ && \
    rm /app/liquibase.zip

# Download JDBC driver
RUN curl -o /usr/local/liquibase/lib/neo4j-jdbc-driver.jar -L "https://repo1.maven.org/maven2/org/neo4j/neo4j-jdbc-bolt/4.0.1/neo4j-jdbc-bolt-4.0.1.jar"

# Link Liquibase to PATH
RUN ln -s /usr/local/liquibase/liquibase /usr/local/bin/liquibase

# Pemission to execute liquibase
RUN chmod +x /usr/local/bin/liquibase

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