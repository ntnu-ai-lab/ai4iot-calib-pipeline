import time
from concurrent import futures

import grpc

# import the generated classes :
import model_pb2
import model_pb2_grpc

# Is this needed?
from calibration_manager import CalibrationManager

port = 8061


# create a class to define the server functions, derived from

class CalibrationServicer(model_pb2_grpc.CalibrationServicer):
    manager = CalibrationManager()

    def calibration_train(self, request, context):

        train_params = {'station': request.station,
                        'pollutant': request.pollutant}

        results = self.manager.train(train_params)

        response = model_pb2.CalibTrainResponse(test_rmse=results['rmse_test'])

        return response

    def calibration_predict(self, request, context):

        sample = {'e6_tiller_pm10': request.e6_tiller_pm10,
                  'e6_tiller_pm25': request.e6_tiller_pm25,
                  'elgeseter_pm10': request.elgeseter_pm10,
                  'elgeseter_pm25': request.elgeseter_pm25,
                  'torvet_pm10': request.torvet_pm10,
                  'torvet_pm25': request.torvet_pm25}

        predicted_aq = self.manager.predict(sample)

        response = model_pb2.CalibPredictResponse()

        if predicted_aq == 0:
            response.predicted_aq_level = 'LOW'
        elif predicted_aq == 1:
            response.predicted_aq_level = 'HIGH'

        return response


# create a grpc server :
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

model_pb2_grpc.add_CalibrationServicer_to_server(CalibrationServicer(), server)

print("Starting server. Listening on port : " + str(port))
server.add_insecure_port("[::]:{}".format(port))
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
