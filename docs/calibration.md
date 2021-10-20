The Calibration module exposes the *calibrate_sample* service, with the following message specification.

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

    // The calibration service receives the current data sample input and outputs the calibrated values for PM2.5 and PM10 for the given sensor.
    message CalibResponse {
      float calibrated_pm25 = 1;
      float calibrated_pm10 = 2;
      DataSample raw_data = 3;
    }

    //Define the service
    service Calibration {
      rpc calibrate_sample(DataSample) returns (CalibResponse);
    }