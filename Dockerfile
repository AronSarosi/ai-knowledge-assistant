# --- Knowledge Assistant container -----------------------------------------
# A container is this whole app sealed into one portable box: the right Python,
# every library, the code, and the run command. It runs identically on a laptop,
# on Cloud Run, or in a client's cloud - no "works on my machine" surprises.

# A mature, slim base. Your laptop runs Python 3.14 (very new - some libraries
# lack ready-made installers for it yet); 3.12 has wheels for everything here.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies FIRST, on their own layer. Docker caches layers, so as
# long as requirements.txt is unchanged this slow step is reused and only code
# changes trigger a fast rebuild.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now the application code and the sample knowledge base.
COPY . .

# Run as a non-root user - standard safety practice in containers.
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# Cloud Run supplies the port to listen on via $PORT (8080 by default). The app
# must bind 0.0.0.0 (all interfaces). HTTPS is handled by the platform in front.
ENV PORT=8080
EXPOSE 8080

# Shell form so $PORT expands at start. The CORS/XSRF flags are off because
# Cloud Run's proxy sits in front and would otherwise block the websocket.
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
