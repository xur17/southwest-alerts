FROM        python:3.5.3-slim

COPY        requirements.txt /tmp/
RUN         pip3 install -r /tmp/requirements.txt

COPY        . /app
ENV         PYTHONPATH /app

ENTRYPOINT  ["python3", "/app/southwestalerts/app.py"]
