import time
from concurrent import futures

import grpc

# import the generated classes :
import model_pb2
import model_pb2_grpc

# import the function we made :
port = 8061
# create a class to define the server functions, derived from

class AI4IoTServicer(model_pb2_grpc.AI4IoTServicer):
    manager = None

    def predict_aq_level(self, request, context):
              
        response = model_pb2.AQPredictResponse()
              
        if(request.current_pm10 < 30):
            response.predicted_aq_level = 'LOW'
        elif(30 <= request.current_pm10 < 50):
            response.predicted_aq_level = 'MEDIUM'
        elif(50 <= request.current_pm10 < 150):
            response.predicted_aq_level = 'HIGH'
        elif(150 <= request.current_pm10):
            response.predicted_aq_level = 'VERY HIGH'
        
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
