FROM python:3.10 as base

WORKDIR /app

COPY requirements.txt .

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir \
     && apt-get update && apt-get -y install cron \
     && mkfifo --mode 0666 /var/log/cron.log

COPY crontab /etc/cron.d/
RUN /usr/bin/crontab /etc/cron.d/crontab

COPY . .

RUN chmod 0744 /app/run.sh

CMD ["/bin/bash", "-c", "printenv >> /etc/environment && cron && tail -f /var/log/cron.log"]
