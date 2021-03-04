FROM ubuntu 

MAINTAINER Tiago Veiga

RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
COPY ./requirements.txt /requirements.txt

COPY model.proto aq_prediction_server.py ./

COPY trained_model/classification_only_pm ./trained_model/classification_only_pm

WORKDIR /

RUN pip3 install -r requirements.txt

RUN python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. model.proto

ENTRYPOINT [ "python3","aq_prediction_server.py" ]