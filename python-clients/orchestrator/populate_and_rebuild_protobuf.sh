cp ../../calibration/calibration.proto calibration.proto
cp ../../data-client/client.proto client.proto

python3 -m grpc_tools.protoc --python_out=. --proto_path=. --grpc_python_out=. *.proto
