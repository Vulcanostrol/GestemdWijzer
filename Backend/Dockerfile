FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Set non-sensitive environment variables
ARG APP_ENV=dev
ARG AUTH_TOKENS

ENV APP_ENV=${APP_ENV} \
    AUTH_TOKENS=${AUTH_TOKENS} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && pip install --upgrade pip

COPY requirements /app/requirements
RUN pip install --no-cache-dir -r requirements/default.txt

COPY . .

RUN chmod +x /usr/local/bin/uvicorn

RUN useradd -m apiserver && chown -R apiserver:apiserver /app
USER apiserver

EXPOSE 80

CMD ["/usr/local/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
