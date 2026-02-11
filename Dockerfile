FROM python:3.11-slim

LABEL maintainer="jy02140251"
LABEL description="Python API Toolkit - Reusable components for building REST APIs"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "pytest", "tests/", "-v"]