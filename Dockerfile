FROM        python:3.5.3-slim

RUN         apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

COPY        requirements.txt /tmp/
RUN         pip3 install -r /tmp/requirements.txt

COPY        . /app
ENV         PYTHONPATH /app

ENTRYPOINT  ["python3", "/app/southwestalerts/app.py"]
