## Dockerfile for nlp service ##
## Author: Piotr Dura ##

FROM tiangolo/uvicorn-gunicorn:python3.8 AS ug

FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-devel AS pytorch

WORKDIR /workspace

# Install apt requirements
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget

# Install python requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy from uvicorn_gunicorn
COPY --from=ug /start.sh /start.sh
RUN chmod +x /start.sh
COPY --from=ug /gunicorn_conf.py /gunicorn_conf.py
COPY --from=ug /start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

# Copy app
COPY ./app /app
WORKDIR /app

EXPOSE 8000

CMD ["/start.sh"]
