import time
from concurrent import futures

import grpc

# import the generated classes :
import model_pb2
import model_pb2_grpc

import joblib
model_filepath = 'models/classification_only_pm.pkl'

port = 8061
# create a class to define the server functions, derived from

class AI4IoTServicer(model_pb2_grpc.AI4IoTServicer):
    manager = None

    #Load RF classifier
    trained_model = joblib.load(model_filepath)

    def predict_aq_level(self, request, context):
              
        response = model_pb2.AQPredictResponse()

        predicted_aq = self.trained_model.predict([[request.e6_tiller_pm10,
                                request.e6_tiller_pm25,
                                request.elgeseter_pm10,
                                request.elgeseter_pm25,
                                request.torvet_pm10,
                                request.torvet_pm25]])

        if predicted_aq == 0:
            response.predicted_aq_level = 'LOW'
        elif predicted_aq == 1:
            response.predicted_aq_level = 'HIGH'
        
        return response

# create a grpc server :
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

model_pb2_grpc.add_AI4IoTServicer_to_server(AI4IoTServicer(), server)

print("Starting server. Listening on port : " + str(port))
server.add_insecure_port("[::]:{}".format(port))
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
