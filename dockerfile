FROM python:3.13-alpine
LABEL maintainer="gabrieldelimaafonso@gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

COPY picpay /picpay
COPY scripts /scripts

WORKDIR /picpay

RUN chmod +x /scripts/commands.sh && \
  chmod -R a+rw /picpay


EXPOSE 8000

RUN python -m venv /venv && \
  /venv/bin/pip install --upgrade pip && \
  /venv/bin/pip install -r /picpay/requirements.txt && \
  adduser --disabled-password --no-create-home duser

ENV PATH="/venv/bin:/scripts:${PATH}"

CMD ["commands.sh"]
