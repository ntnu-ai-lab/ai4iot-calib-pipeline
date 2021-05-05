from timeit import default_timer as timer
import grpc

# import the generated classes
import model_pb2
import model_pb2_grpc

##Main code##
start_ch = timer()
port_addr = "localhost:8061"

# open a gRPC channel
channel = grpc.insecure_channel(port_addr)

# create a stub (client)
stub = model_pb2_grpc.AI4IoTStub(channel)

request = model_pb2.AQTrainRequest(station='elgeseter',
                                   pollutant='pm2.5',
                                   threshold=30,
                                   use_temporal = False,
                                   use_delta = False,
                                   use_only_pm = True,
                                   use_weather = False,
                                   use_forecast = False,
                                   use_traffic = False)
####First, train the model (for now, this is just loading the pre-trained)
response = stub.train_classifier(request)

print('Trained classifier:')
print('Recall = %.2f, Precision = %.2f, ROC = %.2f' % (response.test_recall,response.test_precision,response.test_roc))
