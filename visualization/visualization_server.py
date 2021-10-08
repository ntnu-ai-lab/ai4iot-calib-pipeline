import time
from concurrent import futures
import grpc

import visualization_pb2
import visualization_pb2_grpc

from flask import Flask, render_template
from datetime import datetime
import pytz

port = 8061

tz = pytz.timezone('Europe/Oslo')


class CalibApp():
    def __init__(self):
        self.app = Flask('calib')
        self.app.add_url_rule('/', 'index', self.index)

        self.pm25 = 0
        self.pm10 = 0
        self.update_time = 0

    def index(self):
        return render_template('index.html', calib_pm25=self.pm25, calib_pm10=self.pm10, update_time=self.update_time)

    def get_app(self):

        return self.app

    def set_values(self, new_pm25, new_pm10):
        self.pm25 = new_pm25
        self.pm10 = new_pm10

        now = datetime.now(tz)
        self.update_time = now.strftime("%H:%M:%S")


class VisualizationServicer(visualization_pb2_grpc.VisualizationServicer):

    def set_values(self, request, context):
        myapp.set_values(request.calibrated_pm25, request.calibrated_pm10)

        context.set_details('No more data available')
        context.set_code(grpc.StatusCode.NOT_FOUND)

        return visualization_pb2.Empty()


myapp = CalibApp()
calib_app = myapp.get_app()

# create a grpc server :
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

visualization_pb2_grpc.add_VisualizationServicer_to_server(VisualizationServicer(), server)

print("Starting server. Listening on port : " + str(port))
server.add_insecure_port("[::]:{}".format(port))
server.start()

# try:
#     while True:
#         time.sleep(86400)
# except KeyboardInterrupt:
#     server.stop(0)

#app.run()
