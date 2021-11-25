import orchestrator_pb2
import orchestrator_pb2_grpc

import grpc

import time
import schedule


def update_data():
    try:
        while True:
            # Fetch data sample from external APIs
            data_sample = data_source_stub.request_update(orchestrator_pb2.Empty())

            # Call pre-trained calibration module
            calib_data = calibration_stub.calibrate_sample(data_sample)

            # Update visualization output
            visualization_stub.set_values(calib_data)

    except Exception as e:
        print("Got an exception ", str(e))

    return


##################################################################
# open a gRPC channel for data client
data_source_channel = grpc.insecure_channel("localhost:8060")
data_source_stub = orchestrator_pb2_grpc.AQDataSourceStub(data_source_channel)

# open a gRPC channel for calibration server
calibration_channel = grpc.insecure_channel("localhost:8061")
calibration_stub = orchestrator_pb2_grpc.CalibrationStub(calibration_channel)

# open a gRPC channel for visualization server
visualization_channel = grpc.insecure_channel("localhost:8062")
visualization_stub = orchestrator_pb2_grpc.VisualizationStub(visualization_channel)

## Implements a scheduler to update the data at a fixed frequency.
## For example, let's say that we want an update every hour at the minute 15 (01:15, 02:15, ..., 10:15, so on)
schedule.every().hour.at(":15").do(update_data)

## Or, do an update every 10 seconds
# schedule.every(10).seconds.do(update_data)

## If a scheduler is desired, the following block needs to be uncommented
##################
try:
    while True:
        schedule.run_pending()
        time.sleep(10)

except Exception as e:
    print("Got an exception ", str(e))
###################

# If one doesn't need/want to run frequent calls, just comment all the scheduling and directly call the method to update the data (i.e., run the pipeline once) as in the following block
###################
# try:
#     update_data()
# except Exception as e:
#     print("Got an exception ", str(e))
###################
