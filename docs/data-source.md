## Configuration file

The Data Source module expects a config file with the credentials to access the microsensor and weather data coming, respectively, from the Span and MET (Norwegian Meteorological Institute) APIs (https://api.lab5e.com/span and https://frost.met.no/index.html). The config file should follow the format below.

      #IOT data
      iot_token=<user token>

      #MET API
      met_id=<user id>

## Get personal credentials

### MET API - Meteorological data

It is possible to request credentials in the [MET API webpage](https://frost.met.no/auth/requestCredentials.html). Follow the instructions in there and use the Client ID in the configuration file.

### Span API - Low-cost sensor data

Low-cost sensor data is not, at the moment, publicly available but expected to be made public in the future. In the meantime, the users who have permission to access the data must obtain an API token in the [lab5e console](https://console.lab5e.com/). After obtaining a token, use it in the configuration file.

## Service

The Data Source module exposes the *request_update* service. It is the entry point for the pipeline and, therefore, receives an Empty message according to the container specification of the AI4EU platform. The structure of the messages and service are as follows.

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

            message Empty {
            }
            
            service AQDataSource {
              rpc request_update(Empty) returns (DataSample);
            }
