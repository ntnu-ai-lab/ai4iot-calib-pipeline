cp ../calibration/model.proto calibration_model.proto

python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto