## Configuration file

The Data Source module expects a config file with the credentials to access the microsensor and weather data coming, respectively, from the Span and MET APIs (https://api.lab5e.com/span and https://frost.met.no/index.html). The config file should follow the format below.

      #IOT data
      iot_token=<user token>

      #MET API
      met_id=<user id>

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
