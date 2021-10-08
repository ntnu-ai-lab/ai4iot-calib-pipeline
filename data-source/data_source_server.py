import time
from concurrent import futures

import grpc

# import the generated classes :
import data_source_pb2
import data_source_pb2_grpc

import google.protobuf.empty_pb2

from data_source_manager import DataSourceManager

import os

port = 8061


def readConfig(filepath):
    address = ''
    token = ''

    config = {}

    try:
        with open(filepath) as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise Exception('Config file not found!')
        #return {'iot_api': address, 'iot_token': token}
    lines = [line.strip() for line in lines]
    lineno = 0
    for line in lines:
        lineno += 1
        if len(line) == 0 or line[0] == '#':
            # ignore comments and empty lines
            continue
        words = line.split('=', 1)
        if len(words) != 2:
            raise Exception('Not a key value expression on line {0} in {1}: {2}'.format(lineno, filepath, line))
        if words[0] == 'iot_api':
            config['iot_api'] = words[1]
        elif words[0] == 'iot_token':
            config['iot_token'] = words[1]
        elif words[0] == 'met_id':
            config['met_id'] = words[1]
        else:
            raise Exception('Unknown keyword on line {0} in {1}: {2}'.format(lineno, filepath, line))
    return config


class DataSourceServicer(data_source_pb2_grpc.AQDataSourceServicer):

    def __init__(self):
        self.first_call = True
        self.throw_grpc_error = False

    def init_config(self):
        config = readConfig('/config/.aqdata')
        self.manager = DataSourceManager(config)

        self.first_call = False

    def request_update(self, request, context):
        # config = {'iot_api': request.iot_api,
        #          'iot_token': request.iot_token,
        #          'met_id': request.met_id}

        if self.first_call:
            self.init_config()

        data = self.manager.collect_sample()

        response = data_source_pb2.DataSample1()

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

        # if not self.throw_grpc_error:
        #     data = self.manager.collect_sample()

        #     response = data_source_pb2.DataSample1()

        #     response.pm1 = data['pm1_iot']
        #     response.pm25 = data['pm25_iot']
        #     response.pm10 = data['pm10_iot']
        #     response.air_temperature = data['temperature']
        #     response.relative_humidity = data['humidity']
        #     response.precipitation = data['precipitation']
        #     response.air_pressure = data['air_pressure']
        #     response.wind_speed = data['wind_speed']
        #     response.wind_direction = data['wind_direction']

        #     self.throw_grpc_error = True

        #     return response

        # else:
        #     # Testing grpc error handling (needed for AI4EU pipeline)
        #     # TODO: adapt code to return error code after 1 data request (or decide how to do data managing otherwise)

        #     self.throw_grpc_error = False

        #     return data_source_pb2.DataSample1()


shared_folder = os.getenv("SHARED_FOLDER_PATH")
if shared_folder is not None:
    print("Shared folder is:" + str(shared_folder))
else:
    print("Shared folder non existing")

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
