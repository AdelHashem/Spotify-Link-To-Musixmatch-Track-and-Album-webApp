FROM ubuntu:latest
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 8000
ENTRYPOINT [ "hypercorn", "--bind", "0.0.0.0:8000" , "app:app" ]