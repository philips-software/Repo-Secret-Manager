FROM python:3.9.6

WORKDIR /app
ADD ./entrypoint.sh /app/
ADD ./main.py /app/
RUN pip install requests pygithub
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
