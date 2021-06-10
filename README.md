# ai4iot-acumos

This repository implements modules towards the pipeline for the AI4IoT pilot, using the Acumos infrastructure from the AI4EU platform. Eventually, it will include several services. Currently, only includes the calibration service.

# Calibration
The calibrating service implements the calibration of low-cost sensors in Trondheim. As a proof of concept, it is now deployed with a model trained for the Elgeseter sensor. It receives the readings from the low-cost sensor and weather features (check calibration.proto for which ones are used).

## Running
### 1) Run the server
First, the docker container needs to be built.
`cd calibration && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

### 2) Run the client
Before running the client, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)
`cd ../clients && ./populate_and_rebuild_protobuf.sh`

Finally, the client script can be run which will trigger the communication with the APIs to fetch data and transmit them to the calibration service. Currently the code uses the schedule package to implement a period update on the calibrated values, which are printed in the shell.
`./run-train-client.sh`

**Note**: the clients need protobuf and grpcio-tools python packages installed.
