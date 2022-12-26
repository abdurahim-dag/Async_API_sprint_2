FROM python:3.10 as base

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    && rm requirements.txt

COPY ./start.sh ./start.sh
COPY ./gunicorn_conf.py ./gunicorn_conf.py
RUN chmod +x ./start.sh


FROM base as prod

ARG appuser
RUN useradd -U $appuser

RUN chown $appuser:$appuser -R /app

USER $appuser

COPY --chown=$appuser ./src .

ENTRYPOINT ["/app/start.sh"]


FROM base as dev
WORKDIR /app
CMD [ "uvicorn", "main:app", "--reload"]
