import time
from concurrent import futures

import grpc

# import the generated classes :
import client_pb2
import client_pb2_grpc

import google.protobuf.empty_pb2

from client_manager import DataClientManager

port = 8060


class DataClientServicer(client_pb2_grpc.DataClientServicer):

    def init_client(self, request, context):
        config = {'iot_api': request.iot_api,
                  'iot_token': request.iot_token,
                  'met_id': request.met_id}

        self.manager = DataClientManager(config)

        response = google.protobuf.empty_pb2.Empty()

        return response

    def get_last_data(self, request, context):

        data = self.manager.collect_sample()

        response = client_pb2.DataSample()

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

client_pb2_grpc.add_DataClientServicer_to_server(DataClientServicer(), server)

print("Starting server. Listening on port : " + str(port))
server.add_insecure_port("[::]:{}".format(port))
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
