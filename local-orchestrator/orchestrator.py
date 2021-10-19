import orchestrator_pb2
import orchestrator_pb2_grpc

import grpc

import os
import time
import schedule
from datetime import datetime


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

# TODO: passage of data onto next modules is coded in the update_data() method, to allow for scheduling

# Implements a scheduler to update the data at a fixed frequency.
# Smaller periods are implemented for testing, the final deployment should update every hour. For instance, at the minute 15 every hour to allow every API to update its data.
schedule.every(5).seconds.do(update_data)
# schedule.every().hour.at(":05").do(update_data)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)

except Exception as e:
    print("Got an exception ", str(e))
