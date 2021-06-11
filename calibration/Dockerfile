FROM ubuntu 

MAINTAINER Tiago Veiga

RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
COPY ./requirements.txt /requirements.txt

COPY calibration.proto calibration_server.py calibration_manager.py ./

COPY data ./data

WORKDIR /

RUN pip3 install -r requirements.txt

RUN python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. calibration.proto

RUN useradd calib_user

USER calib_user

ENTRYPOINT [ "python3","calibration_server.py" ]