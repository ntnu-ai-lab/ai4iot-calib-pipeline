# Air quality low cost sensor calibration

This repository implements modules towards the pipeline for the AI4IoT pilot, using the Acumos infrastructure from the AI4EU platform.
Currently, there are three modules which, together, form a pipeline for the calibration of low-cost sensors. The modules are: a `data source` which fetches data from several external APIs and concatenates them, a `calibration` which predicts the true value at the sensor location and a simple `visualization` module which implements a web interface to analyse the output of the calibration procedure.

The modules are prepared to be deployed through the AI4EU Experiments Platform. This means that they are containerized and are ran in Docker containers, expose gRPC services and expects input messages as protobufs.

# Pipeline

![calibration_pipeline_acumos](https://user-images.githubusercontent.com/45718165/137711345-dfa5e2da-10b1-4436-80ca-f2f929b8bd99.png)

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

Go to folder and build the docker container.
`cd data-source && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

Before any call to the data source service, the user must input credentials for some external APIs. The data source server expects a config file named `.aqdata` under the path `/config/.aqdata` with the credentials for the Span and MET APIs (https://span.lab5e.com and https://frost.met.no/index.html), with the format below.

      #IOT data
      iot_token=<user token>

      #MET API
      met_id=<user id>
      
The user can do this with the command `docker cp <orig_file> <container_id>:/config/.aqdata`
*TODO*: describe vars

### Calibration

Go to folder and build the docker container.
`cd calibration && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

### Visualization

Go to folder and build the docker container.
`cd visualization && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

### Orchestration

Orchestrator is the term to the script which connects to all running modules and passes messages forward through the pipeline.

Before running the orchestrator, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)
`cd ../user-clients/orchestrator && ./populate_and_rebuild_protobuf.sh`

## Deployment with AI4EU Experiments Platform (ACUMOS)

Some of the external APIs used by the Data Source component need personal credentials to be accessible. Before running the pipeline, the user needs to input his/her personal credentials into the container. It is expected that the AI4EU Experiments offer this functionality in future versions. For now we have to do it manually.
To prevent any privacy issues this is done locally at runtime with kubernetes copy tools.
`kubectl cp <orig_file> <namespace_id>/<pod_id>:<dest_file>`

### Orchestration

**TODO** Previous step: download solution from platform

**1)** Start minikube

`minikube start`

**2)** Create a new namespace

`kubectl create namespace <name>`

**3)** Run deployment script

`python kubernetes-client-script.py -n <name>`

**4)** 

The user can do this with the command `kubectl cp <orig_file> <namespace_id>/<pod_id>:/config/.aqdata`

It is expected that the AI4EU Experiments offer this functionality in future versions. For now we have to do it manually.

**5)** Run the orchestrator client

Run a single time - `python orchestrator_client <ip>:<port>`

**TODO** run as chronjob

**6)** Visualize the output

The visualization module prints output in the format of an html page available through a webui port in the kubernetes cluster
