import time
from concurrent import futures

import grpc

# import the generated classes :
import data_source_pb2
import data_source_pb2_grpc

from data_source_manager import DataSourceManager

import os

port = 8061


def readConfig(filepath):
    config = {}

    try:
        with open(filepath) as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise Exception('Config file not found!')
        # return {'iot_api': address, 'iot_token': token}
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
        if words[0] == 'iot_token':
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

        self.iot_sensors = {'Elgeseter': '17dh0cf43jg89l',
                            'Torget': '2f3a11687f7a2j'}

    def init_config(self):
        config = readConfig('/config/.aqdata')
        self.manager = DataSourceManager(config, self.iot_sensors)

        self.first_call = False

    def request_update(self, request, context):

        if self.first_call:
            self.init_config()

        data = self.manager.collect_sample()

        response = data_source_pb2.DataSample()

        print(data)

        for sensor in self.iot_sensors:
            sensor_info = response.iot_data.add()

            sensor_info.name = sensor
            sensor_info.pm1 = data[sensor]['pm1_iot']
            sensor_info.pm25 = data[sensor]['pm25_iot']
            sensor_info.pm10 = data[sensor]['pm10_iot']

        response.air_temperature = data['temperature']
        response.relative_humidity = data['humidity']
        response.precipitation = data['precipitation']
        response.air_pressure = data['air_pressure']
        response.wind_speed = data['wind_speed']
        response.wind_direction = data['wind_direction']

        return response

        # if not self.throw_grpc_error:
        #     data = self.manager.collect_sample()

        #     response = data_source_pb2.DataSample()

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
        #     context.set_details('No more data available')
        #     context.set_code(grpc.StatusCode.NOT_FOUND)

        #     self.throw_grpc_error = False

        #     return data_source_pb2.DataSample()


# shared_folder = os.getenv("SHARED_FOLDER_PATH")
# if shared_folder is not None:
#     print("Shared folder is:" + str(shared_folder))
# else:
#     print("Shared folder non existing")

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
