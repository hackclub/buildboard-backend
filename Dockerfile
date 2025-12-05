FROM python:3.11-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
<<<<<<< HEAD
COPY ./.env /code/.env
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "45010"]
=======
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> testing
