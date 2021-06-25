# ai4iot-acumos

This repository implements modules towards the pipeline for the AI4IoT pilot, using the Acumos infrastructure from the AI4EU platform. Eventually, it will include several services. Currently, only the calibration service is developed.

The picture below illustrates the schematic of the pipeline, which includes two modules: one to act as a data broker, i.e., to retrieve data from the APIs of interest (low-cost sensors, weather, etc) and feed it to the services who need it; second, a calibration module which is deployed with a model trained to calibrated low-cost sensor data (currently limited to sensors in Elgeseter and Torget).

![image](https://user-images.githubusercontent.com/45718165/123275711-daa89980-d504-11eb-98b5-ac832add050f.png)

# Data Source
The data source module exposes two services: *initialize* and *request_update*. The first receives the credentials for the APIs which need them (for now Span IoT for low-cost sensors and MET for weather data) and establishes the connections to those APIs. The second can be called anytime the user wants an update on the data.
Important to note that the container provides data updated at every hour on the hour (i.e., at :00).

    message DataSample {
      float pm1 = 1;
      float pm25 = 2;
      float pm10 = 3;
      float air_temperature = 4;
      float relative_humidity = 5;
      float precipitation = 6;
      float air_pressure = 7;
      float wind_speed = 8;
      float wind_direction = 9;
    }

    message InitRequest {
      string iot_api = 1;
      string iot_token = 2;
      string met_id = 3;
    }

    service AQDataSource {
      rpc initialize(InitRequest) returns (google.protobuf.Empty);
      rpc request_update(google.protobuf.Empty) returns (DataSample);
    }

# Calibration
The calibrating service implements the calibration of low-cost sensors in Trondheim. As a proof of concept, it is now deployed with a model trained for the Elgeseter sensor. Currently, the deployed model is trained with low-cost sensor and weather data. Therefore, it expects each sample to include this data.
It exposes the service *calibrate_sample* which receives a data sample (see fields below) and outputs the calibrated values for PM2.5 and PM10.

    message DataSample {
      float pm1 = 1;
      float pm25 = 2;
      float pm10 = 3;
      float air_temperature = 4;
      float relative_humidity = 5;
      float precipitation = 6;
      float air_pressure = 7;
      float wind_speed = 8;
      float wind_direction = 9;
    }

    message CalibResponse {
      float calibrated_pm25 = 1;
      float calibrated_pm10 = 2;
    }

    service Calibration {
      rpc calibrate_sample(DataSample) returns (CalibResponse);
    }

# Running the pipeline

### 1) Run the data source server
Go to folder and build the docker container.
`cd data-source && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

### 2) Run the calibration server
Go to folder and build the docker container.
`cd calibration && ./docker-build.sh`

Then, we can launch the service
`./docker-run.sh`

### 2) Run the orchestrator
Orchestrator is the term to the script which connects to all running modules and passes messages forward through the pipeline.

Before running the orchestrator, it is needed to copy the protobuf message definitions to its folder and compile locally (the client needs to be aware of the message types)
`cd ../user-clients/orchestrator && ./populate_and_rebuild_protobuf.sh`

Before running the orchestrator, two important notes:
- The script expects a config file named `.aqdata` under the home folder (`/home/<username>/.aqdata`) with the credentials for the Span and MET APIs (https://span.lab5e.com and https://frost.met.no/index.html), with the format below.

      #IOT data
      iot_token=<user token>

      #MET API
      met_id=<user id>
      
- The orchestrator implements a scheduler to call the pipeline at a fixed frequency. For illustrative purposes it now requests udpated data to the pipeline every 10 seconds, in real delpoyment it will make sense to update every hour, some minutes after the hour.

      schedule.every(10).seconds.do(update_data) -> update every 10 seconds
      schedule.every().hour.at(":05").do(update_data) -> update every hour at :05 minutes
 

Finally, the orchestrator script can be run which will trigger the communication through the pipeline.
`./run-orchestrator.sh`

Info about the data samples will be printed in the shell, in the format below:

    Current Time = 15:09:45

    (Uncalibrated) data sample is:
    pm1: 0.5887464284896851
    pm25: 1.7239444255828857
    pm10: 8.807469367980957
    air_temperature: 14.800000190734863
    relative_humidity: 65.0
    air_pressure: 1003.9000244140625
    wind_speed: 1.7999999523162842
    wind_direction: 344.0


    Calibrated values are:
    PM2.5: 5.343422889709473
    PM10: 29.775833129882812

**Note**: the orchestrator need protobuf and grpcio-tools python packages installed.

# Other remarks
There is also the possibility to only containerize the calibration service and do all the data fetching in the client side. This is what is implemented in the  `user-clients/calibration-only-client`folder. For now development is focused in the pipeline version, this might be an alternative.

Also, the final goal is to do orchestration automatically through the AI4EU Experiments platform.
