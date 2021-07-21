FROM python:3.8-slim-buster

COPY entrypoint.sh /entrypoint.sh
COPY main.py /main.py

RUN pip install pygithub requests
RUN chmod +x /entrypoint.sh 

ENTRYPOINT ["/entrypoint.sh"]
