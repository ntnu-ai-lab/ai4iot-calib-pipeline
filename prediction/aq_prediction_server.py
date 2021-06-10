import time
from concurrent import futures

import grpc

# import the generated classes :
import model_pb2
import model_pb2_grpc

from classifier_manager import ClassifierManager

port = 8061
# create a class to define the server functions, derived from

class AI4IoTServicer(model_pb2_grpc.AI4IoTServicer):
    manager = ClassifierManager()

    def train_classifier(self, request, context):

        train_params = {'station': request.station,
                        'pollutant': request.pollutant,
                        'threshold': request.threshold,
                        'use_temporal': request.use_temporal,
                        'use_delta': request.use_delta,
                        'use_only_pm': request.use_only_pm,
                        'use_weather': request.use_weather,
                        'use_forecast': request.use_forecast,
                        'use_traffic': request.use_traffic}
        
        results = self.manager.train(train_params)
        
        response = model_pb2.AQTrainResponse(test_recall=results['recall'],
                                             test_precision=results['precision'],
                                             test_roc=results['roc'])

        return response
        

    def predict_aq_level(self, request, context):

        sample = {'e6_tiller_pm10':request.e6_tiller_pm10,
                  'e6_tiller_pm25':request.e6_tiller_pm25,
                  'elgeseter_pm10':request.elgeseter_pm10,
                  'elgeseter_pm25':request.elgeseter_pm25,
                  'torvet_pm10':request.torvet_pm10,
                  'torvet_pm25':request.torvet_pm25}
                                
        predicted_aq = self.manager.predict(sample)

        response = model_pb2.AQPredictResponse()
        
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
