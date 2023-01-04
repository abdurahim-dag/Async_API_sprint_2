#!/usr/bin/env bash
# LF will be replaced by CRLF

set -e

uwsgi --strict --ini /app/uwsgi/uwsgi.ini
