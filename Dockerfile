FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl wget && rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
COPY ./jobs /code/jobs
COPY ./alembic /code/alembic
COPY ./alembic.ini /code/alembic.ini
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "45010"]
