# Builder stage
FROM python:3.12-slim as builder

# Install Poetry
RUN pip install poetry==1.4.2

# Set Poetry environment variables
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy project files
COPY pyproject.toml poetry.lock ./
RUN touch README.md

# Install dependencies using Poetry with caching
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

# Runtime stage
FROM python:3.12-slim as runtime

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    # WeasyPrint dependencies
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Font config
    fonts-dejavu \
    fonts-freefont-ttf \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
ENV VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH"

# Copy the virtual environment from the builder stage
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy the application code
COPY ./app ./app

# Entrypoint for FastAPI
ENTRYPOINT ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "5000"]
