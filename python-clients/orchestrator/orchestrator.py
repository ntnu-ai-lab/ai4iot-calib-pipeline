import client_pb2
import client_pb2_grpc
import calibration_pb2
import calibration_pb2_grpc

import grpc

import google.protobuf.empty_pb2

import os
import time
import schedule
from datetime import datetime


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


def update_data():
    data = data_client_stub.get_last_data(google.protobuf.empty_pb2.Empty())

    calib_data = calibration_stub.calibrate_sample(data)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    print()
    
    #print('Uncalibrated values are:')
    #print("PM2.5: {}".format(data.pm25))
    #print("PM10: {}".format(data.pm10))
    print(data)
    print()

    print("Calibrated values are:")
    print("PM2.5: {}".format(calib_data.calibrated_pm25))
    print("PM10: {}".format(calib_data.calibrated_pm10))
    print()

    return


##################################################################
# open a gRPC channel for data client
data_client_channel = grpc.insecure_channel("localhost:8060")
data_client_stub = client_pb2_grpc.DataClientStub(data_client_channel)

# open a gRPC channel for calibration server
calibration_channel = grpc.insecure_channel("localhost:8061")
calibration_stub = calibration_pb2_grpc.CalibrationStub(calibration_channel)

# Build the request message
request = client_pb2.ClientInitRequest()

# A config file is requested for personal data (for instance, tokens for APIs).
# Currently, the code reads from the ~/.aqdata (i.e., the file .aqdata is in the home directoy).
# TODO: allow the user to input the path to the config file
config = readConfig(getFullPath('.aqdata'))

# Currently, only two APIs need a personal account (Lab5e's Span for the microsensor and MET for meteorological data)
request.iot_api = config['iot_api']
request.iot_token = config['iot_token']
request.met_id = config['met_id']

try:
    data_client_stub.init_client(request)

    # Implements a scheduler to update the data at a fixed frequency.
    # Smaller periods are implemented for testing, the final deployment should update every hour. For instance, at the minute 15 every hour to allow every API to update its data.
    schedule.every(30).seconds.do(update_data)
    # schedule.every().hour.at(":05").do(update_data)

    while True:
        schedule.run_pending()
        time.sleep(2)

except Exception as e:
    print("Got an exception ", str(e))
