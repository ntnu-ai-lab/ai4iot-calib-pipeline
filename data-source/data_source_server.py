import time
from concurrent import futures

import grpc

# import the generated classes :
import data_source_pb2
import data_source_pb2_grpc

from data_source_manager import DataSourceManager

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

        self.nilu_sensors = []

    def init_config(self):
        config = readConfig('/config/.aqdata')

        self.manager = DataSourceManager(config=config,
                                         iot_sensors=self.iot_sensors,
                                         nilu_sensors=self.nilu_sensors)

        self.first_call = False

    def request_update(self, request, context):

        if self.first_call:
            self.init_config()

        try:
            iot_data, met_data, nilu_data = self.manager.collect_sample()
        except ValueError as e:
            print("Got an exception", str(e))
            raise ValueError(e)

        response = data_source_pb2.DataSample()

        for sensor in self.iot_sensors:
            sensor_info = response.iot_data.add()

            sensor_info.name = sensor
            sensor_info.pm1 = iot_data[sensor]['pm1_iot']
            sensor_info.pm25 = iot_data[sensor]['pm25_iot']
            sensor_info.pm10 = iot_data[sensor]['pm10_iot']

        response.air_temperature = met_data['temperature']
        response.relative_humidity = met_data['humidity']
        response.precipitation = met_data['precipitation']
        response.air_pressure = met_data['air_pressure']
        response.wind_speed = met_data['wind_speed']
        response.wind_direction = met_data['wind_direction']

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
