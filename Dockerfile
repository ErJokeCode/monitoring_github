FROM python:3.13.2-alpine

RUN apk update && apk add --no-cache curl

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ ./src/
COPY ./alembic.ini .
COPY ./entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "./src/main.py"]