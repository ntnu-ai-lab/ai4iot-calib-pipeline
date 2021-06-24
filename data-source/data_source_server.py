import time
from concurrent import futures

import grpc

# import the generated classes :
import data_source_pb2
import data_source_pb2_grpc

import google.protobuf.empty_pb2

from data_source_manager import DataSourceManager

port = 8060


class DataSourceServicer(data_source_pb2_grpc.AQDataSourceServicer):

    def initialize(self, request, context):
        config = {'iot_api': request.iot_api,
                  'iot_token': request.iot_token,
                  'met_id': request.met_id}

        self.manager = DataSourceManager(config)

        response = google.protobuf.empty_pb2.Empty()

        return response

    def request_update(self, request, context):

        data = self.manager.collect_sample()

        response = data_source_pb2.DataSample()

        response.pm1 = data['pm1_iot']
        response.pm25 = data['pm25_iot']
        response.pm10 = data['pm10_iot']
        response.air_temperature = data['temperature']
        response.relative_humidity = data['humidity']
        response.precipitation = data['precipitation']
        response.air_pressure = data['air_pressure']
        response.wind_speed = data['wind_speed']
        response.wind_direction = data['wind_direction']

        return response


# create a grpc server :
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

data_source_pb2_grpc.add_AQDataSourceServicer_to_server(DataSourceServicer(), server)

print("Starting server. Listening on port : " + str(port))
server.add_insecure_port("[::]:{}".format(port))
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
