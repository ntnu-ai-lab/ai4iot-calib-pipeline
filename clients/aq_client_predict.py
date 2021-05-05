from random import randint
from timeit import default_timer as timer
import pandas as pd

import grpc

# import the generated classes
import model_pb2
import model_pb2_grpc

### Define a method to get last observations from NILU. This gets observations for all stations in the city (API only has the option to fetch data for a single station for historical data)
def get_last_nilu_obs():
    url = 'https://api.nilu.no/aq/utd?areas=trondheim&components=pm10;pm2.5'
    data = pd.DataFrame.from_records(pd.read_json(url))[['station','component','toTime','value','index']]
    
    return data
###################


##Main code##
start_ch = timer()
port_addr = "localhost:8061"

# open a gRPC channel
channel = grpc.insecure_channel(port_addr)

# create a stub (client)
stub = model_pb2_grpc.AI4IoTStub(channel)

#Fetch last measurements from NILU API; returns a dataframe with ['station', 'component', 'toTime', 'value', 'index'] as column keys
df_last_obs = get_last_nilu_obs()

#Build the request message
request = model_pb2.AQPredictRequest()
request.e6_tiller_pm10 = df_last_obs.loc[(df_last_obs['station']=='E6-Tiller') & (df_last_obs['component']=='PM10'),'value'].iloc[0]
request.e6_tiller_pm25 = df_last_obs.loc[(df_last_obs['station']=='E6-Tiller') & (df_last_obs['component']=='PM2.5'),'value'].iloc[0]
request.elgeseter_pm10 = df_last_obs.loc[(df_last_obs['station']=='Elgeseter') & (df_last_obs['component']=='PM10'),'value'].iloc[0]
request.elgeseter_pm25 = df_last_obs.loc[(df_last_obs['station']=='Elgeseter') & (df_last_obs['component']=='PM2.5'),'value'].iloc[0]
request.torvet_pm10 = df_last_obs.loc[(df_last_obs['station']=='Torvet') & (df_last_obs['component']=='PM10'),'value'].iloc[0]
request.torvet_pm25 = df_last_obs.loc[(df_last_obs['station']=='Torvet') & (df_last_obs['component']=='PM2.5'),'value'].iloc[0]

response = stub.predict_aq_level(request)

print('Current PM2.5 in Elgeseter is %.2f' % request.elgeseter_pm25)
print('Predicted PM2.5 AQ level in the next 24 hours is {}'.format(response.predicted_aq_level))

print('Done!')
