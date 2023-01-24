FROM python:latest
COPY src .
RUN pip install requests hashlib flask
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]