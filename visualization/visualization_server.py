import time
from concurrent import futures
import grpc

import visualization_pb2
import visualization_pb2_grpc

from flask import Flask, render_template
from datetime import datetime
import pytz

import plotly
import plotly.graph_objs as go
import plotly.express as px

import numpy as np
import pandas as pd
import json

from collections import deque

port = 8061

tz = pytz.timezone('Europe/Oslo')

history_length = 12


class CalibApp():
    def __init__(self):
        self.app = Flask('calib')
        self.app.add_url_rule('/', 'index', self.index)

        self.pm25 = 0
        self.pm10 = 0
        self.update_time = 0

        self.history_pm25 = deque(maxlen=history_length)
        self.history_pm10 = deque(maxlen=history_length)
        self.history_raw_pm25 = deque(maxlen=history_length)
        self.history_raw_pm10 = deque(maxlen=history_length)
        self.history_time_index = deque(maxlen=history_length)

    def index(self):
        if not self.history_time_index:  # If history is empty return warning html
            bar_pm25 = None
            bar_pm10 = None
        else:  # Otherwise just plot whatever we have received
            bar_pm25, bar_pm10 = self.create_plot()

        return render_template('index.html', calib_pm25=self.pm25, calib_pm10=self.pm10, update_time=self.update_time, plot_pm25=bar_pm25, plot_pm10=bar_pm10)

    def get_app(self):

        return self.app

    def set_values(self, new_pm25, new_pm10, raw_pm25, raw_pm10):
        self.pm25 = new_pm25
        self.pm10 = new_pm10

        now = datetime.now(tz)
        self.update_time = now.strftime("%H:%M:%S")

        self.history_pm25.append(new_pm25)
        self.history_pm10.append(new_pm10)
        self.history_raw_pm25.append(raw_pm25)
        self.history_raw_pm10.append(raw_pm10)
        self.history_time_index.append(self.update_time)

    def create_plot(self):

        # Create plot for PM2.5 history
        data_pm25 = px.line(y=[list(self.history_pm25), list(self.history_raw_pm25)],
                            x=list(self.history_time_index),
                            labels={'x': 'Time', 'y': 'Calibrated value', 'variable': 'Source'},
                            title='PM2.5 History')
        data_pm25.data[1].name = 'Raw'
        data_pm25.data[0].name = 'Calibrated'

        graphJSON_pm25 = json.dumps(data_pm25, cls=plotly.utils.PlotlyJSONEncoder)

        # Create plot for PM10 history
        data_pm10 = px.line(y=[list(self.history_pm10), list(self.history_raw_pm10)],
                            x=list(self.history_time_index),
                            labels={'x': 'Time', 'y': 'Calibrated value', 'variable': 'Source'},
                            title='PM10 History')

        data_pm10.data[1].name = 'Raw'
        data_pm10.data[0].name = 'Calibrated'

        graphJSON_pm10 = json.dumps(data_pm10, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON_pm25, graphJSON_pm10


class VisualizationServicer(visualization_pb2_grpc.VisualizationServicer):

    def set_values(self, request, context):
        myapp.set_values(request.calibrated_pm25, request.calibrated_pm10, request.raw_data.pm25, request.raw_data.pm10)

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
