from timeit import default_timer as timer
import grpc

# import the generated classes
import calibration_model_pb2
import calibration_model_pb2_grpc

##Main code##
start_ch = timer()
port_addr = "localhost:8061"

# open a gRPC channel
channel = grpc.insecure_channel(port_addr)

# create a stub (client)
stub = calibration_model_pb2_grpc.CalibrationStub(channel)

request = calibration_model_pb2.CalibTrainRequest(station='elgeseter',
                                                  pollutant='pm25')

####First, train the model (for now, this is just loading the pre-trained)
response = stub.calibration_train(request)

print('Trained classifier:')
print('Test RMSE: ', response.rmse)
# print('rmse = %.2f, r2 score = %.2f' % (response.test_rmse, response.test_r2))
