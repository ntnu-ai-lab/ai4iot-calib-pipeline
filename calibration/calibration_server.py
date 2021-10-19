import time
from concurrent import futures

import grpc

# import the generated classes :
import calibration_pb2
import calibration_pb2_grpc

import numpy as np

from calibration_manager import CalibrationManager

port = 8061

# create a class to define the server functions, derived from


class CalibrationServicer(calibration_pb2_grpc.CalibrationServicer):
    manager = CalibrationManager()

    def calibrate_sample(self, request, context):

        sample = {'pm1': request.pm1,
                  'pm25': request.pm25,
                  'pm10': request.pm10,
                  'air_temperature': request.air_temperature,
                  'relative_humidity': request.relative_humidity,
                  'precipitation': request.precipitation,
                  'air_pressure': request.air_pressure,
                  'wind_speed': request.wind_speed,
                  'wind_direction': request.wind_direction}

        response = calibration_pb2.CalibResponse()

        response.calibrated_pm25, response.calibrated_pm10 = self.manager.predict(np.array(list(sample.values())).reshape(1, -1))

        response.raw_data.pm25 = request.pm25
        response.raw_data.pm10 = request.pm10

        return response


# create a grpc server :
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

calibration_pb2_grpc.add_CalibrationServicer_to_server(CalibrationServicer(), server)

print("Starting server. Listening on port : " + str(port))
server.add_insecure_port("[::]:{}".format(port))
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
