## Service

The Visualization module exposes the *set_values* service, which receives the raw and calibrated data and outputs a simple web interface for exposure of the data passing through the pipeline. The message and service structure are as follows. Since this module is the last in the pipeline, its output if an Empty message.

        message CalibratedSample {
          float raw_pm1 = 1;
          float raw_pm25 = 2;
          float raw_pm10 = 3;
          float calibrated_pm25 = 4;
          float calibrated_pm10 = 5;
          string sensor_name = 6;
        }

        message CalibratedData {
          repeated CalibratedSample data = 1;
        }

        message Empty {
        }

        service Visualization {
          rpc set_values(CalibratedData) returns (Empty);
        }
