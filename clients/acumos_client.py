import os
from datetime import datetime
import schedule
import time

import grpc

# import the generated classes
import calibration_pb2
import calibration_pb2_grpc

from api_clients.client_iot import ClientIot
from api_clients.client_nilu import ClientNilu
from api_clients.client_met import ClientMet


def getFullPath(filename):
    home = os.path.expanduser("~")
    return os.path.join(home, filename)


def readConfig(filepath):
    address = ''
    token = ''

    config = {}

    try:
        with open(filepath) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {'iot_api': address, 'iot_token': token}
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


class ClientManager():
    def __init__(self, config):
        self.config = config
        ## Create api clients
        self.client_iot = ClientIot(addr=config['iot_api'],
                                    token=config['iot_token'])
        self.client_met = ClientMet(client_id=config['met_id'])
        self.client_nilu = ClientNilu()

    def collect_sample(self):
        iot_data = self.client_iot.fetch_last_data(device='17dh0cf43jg89l',
                                                   elements=['pm1','pm25','pm10','opc_temp','opc_hum'],
                                                   mask=['pm1_iot','pm25_iot','pm10_iot','temp_iot','hum_iot'])

        nilu_data = self.client_nilu.fetch_last_data(station='Elgeseter',
                                                     elements=['pm2.5', 'pm10'],
                                                     mask=['pm25_nilu', 'pm10_nilu'])
        
        met_data = self.client_met.fetch_last_data(source='SN68860',
                                                   elements=['air_temperature', 'relative_humidity', 'sum(precipitation_amount PT1H)', 'surface_air_pressure', 'wind_speed', 'wind_from_direction'],
                                                   mask=['temperature', 'humidity', 'precipitation', 'air_pressure', 'wind_speed', 'wind_direction'])

        return {**iot_data, **met_data, **nilu_data}

    def request_calib_service(self, data):
        # start_ch = timer()
        port_addr = "localhost:8061"

        # open a gRPC channel
        channel = grpc.insecure_channel(port_addr)

        # create a stub (client)
        stub = calibration_pb2_grpc.CalibrationStub(channel)

        # Build the request message
        request = calibration_pb2.DataSample()

        # Copy data into request format
        request.pm1 = data['pm1_iot']
        request.pm25 = data['pm25_iot']
        request.pm10 = data['pm10_iot']
        request.air_temperature = data['temperature']
        request.relative_humidity = data['humidity']
        request.precipitation = data['precipitation']
        request.air_pressure = data['air_pressure']
        request.wind_speed = data['wind_speed']
        request.wind_direction = data['wind_direction']

        response = stub.calibrate_sample(request)

        return response.calibrated_pm25, response.calibrated_pm10


def update_calib(manager):

    data = manager.collect_sample()

    calib_pm25, calib_pm10 = manager.request_calib_service(data)

    #####################################
    ## Print info

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    print()

    print('Uncalibrated values are:')
    print("PM2.5: {}".format(data['pm25_iot']))
    print("PM10: {}".format(data['pm10_iot']))

    print()

    print("Calibrated values are:")
    print("PM2.5: {}".format(calib_pm25))
    print("PM10: {}".format(calib_pm10))

    print()

    return


def main():
    config = readConfig(getFullPath('.aqdata'))

    client_manager = ClientManager(config)

    schedule.every().hour.at(":15").do(update_calib, manager=client_manager)
    # schedule.every(1).minutes.do(update_calib, manager=client_manager)

    while True:
        schedule.run_pending()
        time.sleep(5)


main()
