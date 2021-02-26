from random import randint
from timeit import default_timer as timer
import pandas as pd

import grpc

# import the generated classes
import model_pb2
import model_pb2_grpc

### Fetch last value from NILU API
def get_last_nilu_obs(station,component):
    
    url = 'https://api.nilu.no/aq/utd?areas=trondheim&components=pm10;pm2.5'      
    data = pd.DataFrame.from_records(pd.read_json(url))[['station','component','toTime','value','index']]
    #####
    
    measured_val = data[(data['station']==station) & (data['component']==component)]['value'].values[0]
    
    return measured_val
###################


##Main code##
start_ch = timer()
port_addr = "localhost:8061"

# open a gRPC channel
channel = grpc.insecure_channel(port_addr)

# create a stub (client)
stub = model_pb2_grpc.AI4IoTStub(channel)

station = 'E6-Tiller'
component = 'PM10'
measured_val = get_last_nilu_obs(station,component)

print('Current {} level at {} is {}'.format(component,station,measured_val))

request = model_pb2.AQPredictRequest(current_pm10 = measured_val)

response = stub.predict_aq_level(request)

print('Predicted AQ level is {}'.format(response.predicted_aq_level))

print('Done!')
