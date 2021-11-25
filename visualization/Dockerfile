FROM ubuntu 

MAINTAINER Tiago Veiga

RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
COPY ./requirements.txt /requirements.txt

COPY visualization.proto visualization_server.py /

COPY ./templates/* /templates/

WORKDIR /

RUN pip3 install -r requirements.txt

RUN python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. visualization.proto

ENV PYTHONUNBUFFERED=1

EXPOSE 8062

CMD gunicorn -t 0 -b :8062 visualization_server:calib_app