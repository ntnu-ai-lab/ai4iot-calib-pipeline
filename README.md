# ai4iot-acumos

This repository contains modules from the AI4IoT pilot that are intended to use the Acumos infrastructure from the AI4EU platform.

Currently it holds a simple air quality predictions server. It includes a training and predicting services. The former receives some parameters as input (check model.proto in aq-server folder, TODO: describe here all the parameters) and trains a random forest classifier to predict whether the target will be over the threshold in the next 24 hours. The prediction service receives a sample of the features with which the classifier was trained and predicts the pollution level for the next 24 hours.

# Running
## 1) Run the server
First, the docker container needs to be built.
`cd aq-server && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

## 2) Run the client
Before running the client, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)
`cd ../aq-client && ./populate_and_rebuild_protobuf.sh`

Finally, the client scripts can be run. First, the model needs to be trained, so there is a script to call the training service. Input parameters are currently defined inside the python script `aq_train_client-py`. The service returns metrics on the model performance, which are printed by the client script.
`./run-train-client.sh`

Then, we can predict based from current observations. The predict script fetches the last observations from NILU, communicates with the server and prints the predicted AQ level received through the predicting service. (for now it only fetches NILU data, so we cannot actually use models trained with more features. TODO: implement fetching of last observations of other features: weather and traffic)
`./run-predict-client.sh`

**Note**: the clients need protobuf and grpcio-tools python packages installed.
