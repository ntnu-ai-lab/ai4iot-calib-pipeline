FROM ubuntu 

MAINTAINER Tiago Veiga

RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
COPY ./requirements.txt /requirements.txt

COPY client.proto client_server.py client_manager.py ./

COPY api_clients ./api_clients

WORKDIR /

RUN pip3 install -r requirements.txt

RUN python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. client.proto

ENTRYPOINT [ "python3","client_server.py" ]