FROM python:3.10 as base

WORKDIR /app

FROM base as prod

ARG appuser
RUN useradd -U $appuser

RUN  mkdir -p /app/media \
     && chown $appuser:$appuser /app/media \
     && mkdir -p /app/static \
     && chown $appuser:$appuser /app/static \
     && pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir \
     && chown $appuser:$appuser -R /app

USER $appuser

COPY --chown=$appuser . .

ENTRYPOINT ["/app/run.sh"]

FROM base as dev

COPY requirements.txt .

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
