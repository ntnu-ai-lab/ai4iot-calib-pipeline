import time
from concurrent import futures
import grpc

import visualization_pb2
import visualization_pb2_grpc

from flask import Flask, render_template
from datetime import datetime
import pytz

import plotly
import plotly.express as px

import json

from collections import deque

port = 8061

tz = pytz.timezone('Europe/Oslo')

history_length = 12


class CalibApp():
    def __init__(self):
        self.app = Flask('calib')
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/sensor/<name>', 'elgeseter', self.plot_sensor)

        self.data = {'Elgeseter': None,
                     'Torget': None}

        self.data['Elgeseter'] = {'pm25': 0,
                                  'pm10': 0,
                                  'update_time': 0,
                                  'history_pm25': deque(maxlen=history_length),
                                  'history_pm10': deque(maxlen=history_length),
                                  'history_raw_pm25': deque(maxlen=history_length),
                                  'history_raw_pm10': deque(maxlen=history_length),
                                  'history_time_index': deque(maxlen=history_length)}

        self.data['Torget'] = {'pm25': 0,
                               'pm10': 0,
                               'update_time': 0,
                               'history_pm25': deque(maxlen=history_length),
                               'history_pm10': deque(maxlen=history_length),
                               'history_raw_pm25': deque(maxlen=history_length),
                               'history_raw_pm10': deque(maxlen=history_length),
                               'history_time_index': deque(maxlen=history_length)}

        self.plots = {'Elgeseter_pm25': None,
                      'Elgeseter_pm10': None,
                      'Torget_pm25': None,
                      'Torget_pm10': None}

    def index(self):
        return render_template('index.html')

    def plot_sensor(self, name):
        name = name.capitalize()

        return render_template('sensor.html', sensor=name, plot_pm25=self.plots[name + '_pm25'], plot_pm10=self.plots[name + '_pm10'])

    def get_app(self):

        return self.app

    def set_values(self, sensor_name, new_pm25, new_pm10, raw_pm25, raw_pm10):
        self.data[sensor_name]['pm25'] = new_pm25
        self.data[sensor_name]['pm10'] = new_pm10

        now = datetime.now(tz)
        self.data[sensor_name]['update_time'] = now.strftime("%H")

        self.data[sensor_name]['history_pm25'].append(new_pm25)
        self.data[sensor_name]['history_pm10'].append(new_pm10)
        self.data[sensor_name]['history_raw_pm25'].append(raw_pm25)
        self.data[sensor_name]['history_raw_pm10'].append(raw_pm10)
        self.data[sensor_name]['history_time_index'].append(self.data[sensor_name]['update_time'])

        self.plots[sensor_name + '_pm25'], self.plots[sensor_name + '_pm10'] = self.create_plot(sensor_name.capitalize())

    def create_plot(self, sensor_name):

        # Create plot for PM2.5 history
        data_pm25 = px.line(y=[list(self.data[sensor_name]['history_pm25']), list(self.data[sensor_name]['history_raw_pm25'])],
                            x=list(self.data[sensor_name]['history_time_index']),
                            labels={'x': 'Time', 'y': 'Calibrated value', 'variable': 'Source'})
        data_pm25.data[1].name = 'Raw'
        data_pm25.data[0].name = 'Calibrated'

        graphJSON_pm25 = json.dumps(data_pm25, cls=plotly.utils.PlotlyJSONEncoder)

        # Create plot for PM10 history
        data_pm10 = px.line(y=[list(self.data[sensor_name]['history_pm10']), list(self.data[sensor_name]['history_raw_pm10'])],
                            x=list(self.data[sensor_name]['history_time_index']),
                            labels={'x': 'Time', 'y': 'Calibrated value', 'variable': 'Source'})

        data_pm10.data[1].name = 'Raw'
        data_pm10.data[0].name = 'Calibrated'

        graphJSON_pm10 = json.dumps(data_pm10, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON_pm25, graphJSON_pm10


class VisualizationServicer(visualization_pb2_grpc.VisualizationServicer):

    def set_values(self, request, context):
        for sample in request.data:
            myapp.set_values(sample.sensor_name.capitalize(), sample.calibrated_pm25, sample.calibrated_pm10, sample.raw_pm25, sample.raw_pm10)

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
