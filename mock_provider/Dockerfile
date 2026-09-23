FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY mock_provider ./mock_provider

RUN pip install --no-cache-dir .

EXPOSE 9000

CMD ["uvicorn", "mock_provider.main:app", "--host", "0.0.0.0", "--port", "9000"]
