# Air quality low cost sensor calibration

This repository implements modules towards the pipeline for the AI4IoT pilot, using the Acumos infrastructure from the AI4EU platform.
Currently, there are three modules which, together, form a pipeline for the calibration of low-cost sensors. The modules are: a `data source` which fetches data from several external APIs and concatenates them, a `calibration` which predicts the true value at the sensor location and a simple `visualization` module which implements a web interface to analyse the output of the calibration procedure.

The modules are prepared to be deployed through the AI4EU Experiments Platform. This means that they are containerized and are ran in Docker containers, expose gRPC services and expects input messages as protobufs.

# Component description

## Data Source
The Data Source component serves as an aggregator of data incoming from different services, and which is useful for the AI4IoT pipeline. In particular, it connects to external APIs and provides data in an unified (and standardized through protobuf message definition) way.
The AI4IoT tackles air quality in the city of Trondheim, Norway. Therefore, the current version of this component fetches data for this city. The structure can, however, be replicated to any other place by extending the scripts with the given API calls for the place of interest.
Currently, available data through this component is pollution measurements both from a network of low-cost sensors, a (much smaller) network of industrial sensors and meteorological data.

## Calibration
The Calibration component is part of the AI4IoT pipeline. It implements a machine learning model that calibrates data coming from low-cost sensors, such that the output is as close as possible to reference values. The component is deployed with a pre-trained model and outputs the calibrated values for PM2.5 and PM10 measurements. Inputs are PM measurements from the sensor and meteorological data.

## Visualization
The Visualization component implements a simple web interface which presents historical data (for the past 12 hours) of the raw data from a low-cost sensor and the calibrated values.

# Running the pipeline

## Locally with docker

### Data Source

### Calibration

### Visualization

### Orchestration

## Deployment with AI4EU Experiments Platform (ACUMOS)

Some of the external APIs used by the Data Source component need personal credentials to be accessible. Before running the pipeline, the user needs to input his/her personal credentials into the container. It is expected that the AI4EU Experiments offer this functionality in future versions. For now we have to do it manually.
To prevent any privacy issues this is done locally at runtime with kubernetes copy tools.
`kubectl cp <orig_file> <namespace_id>/<pod_id>:<dest_file>`

### Orchestration

# Outdated - Prediction
It includes a training and predicting services. The former receives some parameters as input (check model.proto in prediction folder, TODO: describe here all the parameters) and trains a random forest classifier to predict whether the target will be over the threshold in the next 24 hours. The prediction service receives a sample of the features with which the classifier was trained and predicts the pollution level for the next 24 hours.

## Running
### 1) Run the server
First, the docker container needs to be built.
`cd prediction && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

### 2) Run the client
Before running the client, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)
`cd ../clients && ./populate_and_rebuild_protobuf.sh`

Finally, the client scripts can be run. First, the model needs to be trained, so there is a script to call the training service. Input parameters are currently defined inside the python script `aq_train_client-py`. The service returns metrics on the model performance, which are printed by the client script.
`./run-train-client.sh`

Then, we can predict based from current observations. The predict script fetches the last observations from NILU, communicates with the server and prints the predicted AQ level received through the predicting service. (for now it only fetches NILU data, so we cannot actually use models trained with more features. TODO: implement fetching of last observations of other features: weather and traffic)
`./run-predict-client.sh`

**Note**: the clients need protobuf and grpcio-tools python packages installed.
