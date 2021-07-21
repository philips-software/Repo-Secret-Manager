FROM python:3.8-slim-buster

ADD entrypoint.sh /entrypoint.sh
ADD main.py /main.py

RUN pip install pygithub requests
RUN chmod +x /entrypoint.sh 
RUN pwd 
RUN ls

ENTRYPOINT /entrypoint.sh
