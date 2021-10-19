## Service

The Visualization module exposes the *set_values* service, which receives the raw and calibrated data and outputs a simple web interface for exposure of the data passing through the pipeline. The message and service structure are as follows. Since this module is the last in the pipeline, its output if an Empty message.

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

    message CalibratedValues {
      float calibrated_pm25 = 1;
      float calibrated_pm10 = 2;
      DataSample raw_data = 3;
    }

    message Empty {
    }

    service Visualization {
      rpc set_values(CalibratedValues) returns (Empty);
    }
