FROM python:3.10-slim

RUN pip3 install --no-cache-dir --disable-pip-version-check wheel \
    && pip3 install --no-cache-dir --disable-pip-version-check poetry crcmod

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .
COPY app.py .

# separate poetry install from deps install
RUN poetry install --only=main \
    && rm -rf /root/.cache/pypoetry/cache /root/.cache/pypoetry/artifacts/

# avoid multiprocessing (workers > 1) for now to make instrumentation simpler
ENTRYPOINT ["poetry", "run", "gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "app:app"]
