FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip wheel -r requirements.txt --no-deps -w /wheels

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt
COPY . /app
ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "src/main.py"]
