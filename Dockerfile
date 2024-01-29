# Use a specific tag for a more deterministic build
FROM python:3.10-slim-bullseye as base

# Install dependencies in a single RUN and clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install pip packages in a virtual environment
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

# Use a non-root user for better security
RUN useradd -m appuser

# Create app directory and ensure appuser has full access to it
RUN mkdir /app && chown appuser:appuser /app

# Set the working directory to /app
WORKDIR /app

# Now copy the application files into /app with the correct ownership
COPY --chown=appuser:appuser .streamlit .streamlit
COPY --chown=appuser:appuser app app
COPY --chown=appuser:appuser tmp_data/results/experiments_Oct2023.ddb /app/tmp_data/results/experiments_Oct2023.ddb

# Switch to non-root user
USER appuser

EXPOSE 8080

# Run it!
ENTRYPOINT ["streamlit", "run", "app/ducklit.py", "--server.port=8080", "--server.address=0.0.0.0"]
