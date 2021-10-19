# Air quality low cost sensor calibration

This repository implements modules towards the pipeline for the AI4IoT pilot, using the Acumos infrastructure from the AI4EU platform.
Currently, there are three modules which, together, form a pipeline for the calibration of low-cost sensors. The modules are: a `data source` which fetches data from several external APIs and concatenates them, a `calibration` which predicts the true value at the sensor location and a simple `visualization` module which implements a web interface to analyse the output of the calibration procedure.

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
The [Visualization](docs/visualization) component implements a simple web interface which presents historical data (for the past 12 hours) of the raw data from a low-cost sensor and the calibrated values.

# Deployment instructions

This repository documents two possible alternatives for the depolyment of this pipeline. First we describe how to do it locallly with docker and manual orchestration, with a script written just for this particular case. Finally, the deployment process through the AI4EU Experiments platform (which is based on the Acumos platform) is documented. These are documented in separated files, follow the given links for each of them.

## Locally with docker

[Local deployment with docker tools](docs/docker.md)

## Deployment with AI4EU Experiments Platform (ACUMOS)

[Deployment through the AI4EU Experiments platform](docs/acumos.md)
