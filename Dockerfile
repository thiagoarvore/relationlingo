FROM python:3.13

WORKDIR /relationlingo

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update && apt install -y nano
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /relationlingo/staticfiles /relationlingo/static

COPY . .

EXPOSE 8000
