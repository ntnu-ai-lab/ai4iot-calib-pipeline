# aq-prediction-acumos

This repository implements a simple air quality predictions server, using the Acumos infrastructure from the AI4EU platform.
The service is a warning system, predicting whether the values of PM2.5 will be over 30 ug/m^3 in the next 24 hours.

# Running
## 1) Run the server
First, the docker container needs to be built.
`cd aq-server && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

## 2) Run the client
Before running the client, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)
`cd ../aq-client && ./populate_and_rebuild_protobuf.sh`

Finally, the client script can be run. It will fetch the last observations from NILU, communicate with the server and return the predicted AQ level, which is printed in the shell by the client script.
`./run-client.sh`

**Note**: the client needs protobuf and grpcio-tools python packages installed.
