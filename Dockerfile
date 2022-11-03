FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .
COPY app.py .

RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y -qq build-essential \
    && pip3 install --no-cache-dir --disable-pip-version-check wheel \
    && pip3 install --no-cache-dir --disable-pip-version-check poetry crcmod
# separate poetry install from deps install
RUN poetry install --only=main \
    && rm -rf /root/.cache/pypoetry/cache /root/.cache/pypoetry/artifacts/ \
    && apt-get remove -y -qq build-essential \
    && apt-get autoremove -y -qq

ENV PORT 8080

# avoid multiprocessing (workers > 1) for now to make instrumentation simpler
# use the 'shell' form of entrypoint so variables get evaluated
ENTRYPOINT poetry run gunicorn --bind :${PORT} --workers 1 --threads 8 app:app
