# Air quality low cost sensor calibration

This repository includes the modules for a use case of pipeline deployment based on the AI4EU Experiments platform. The use case is calibration of IoT devices, in this case air quality sensors.
The pipeline is broken down into three three modules which follow a generalizable data flow for different types of architectures with IoT devices. The modules are: a `data source` which fetches data from several external APIs and concatenates them, a `calibration` which predicts the true value at the sensor location and a simple `visualization` module which implements a web interface to analyse the output of the calibration procedure.

The modules are prepared to be deployed through the AI4EU Experiments Platform. This means that they are containerized and are ran in Docker containers, expose gRPC services and expects input messages as protobufs.

# Pipeline

![calibration_pipeline_acumos](https://user-images.githubusercontent.com/45718165/137711345-dfa5e2da-10b1-4436-80ca-f2f929b8bd99.png)

# Component description

## Data Source
The [Data Source](docs/data-source.md) component serves as an aggregator of data incoming from different services, and which is useful for the AI4IoT pipeline. In particular, it connects to external APIs and provides data in an unified (and standardized through protobuf message definition) way.
The AI4IoT tackles air quality in the city of Trondheim, Norway. Therefore, the current version of this component fetches data for this city. The structure can, however, be replicated to any other place by extending the scripts with the given API calls for the place of interest.
Currently, available data through this component is pollution measurements both from a network of low-cost sensors, a (much smaller) network of industrial sensors and meteorological data.

## Calibration
The [Calibration](docs/calibration.md) component is part of the AI4IoT pipeline. It implements a machine learning model that calibrates data coming from low-cost sensors, such that the output is as close as possible to reference values. The component is deployed with a pre-trained model and outputs the calibrated values for PM2.5 and PM10 measurements. Inputs are PM measurements from the sensor and meteorological data.

## Visualization
The [Visualization](docs/visualization.md) component implements a simple web interface which presents historical data (for the past 12 hours) of the raw data from a low-cost sensor and the calibrated values.

# Deployment instructions

This repository documents three possible alternatives for the deployment of this pipeline. First we describe the procedure to deploy locally with docker and manual orchestration (i.e., a script written just for this particular case). Here there are two sub-alternatives, either to build the containers locally from the source code or pull from [Docker Hub](https://hub.docker.com), although the latter is recommended. Finally, the deployment process through the AI4EU Experiments platform (which is based on the Acumos platform) is documented. The following links lead to documentation for each of the alternatives.

## Locally with docker

[Local deployment with docker containers built locally](docs/docker-local.md)

[Local deployment with docker containers pulled from Docker Hub](docs/docker-hub.md)

## Deployment with AI4EU Experiments Platform (ACUMOS)

[Deployment through the AI4EU Experiments platform](docs/acumos.md)
