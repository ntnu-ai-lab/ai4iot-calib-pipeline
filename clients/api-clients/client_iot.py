import time
import requests

import aq_pb2
import base64

import numpy as np


class ClientError(Exception):
    def __init__(self, resp):
        self.http_status_code = resp.status_code
        self.message = resp.text

    def __str__(self):
        return self.message


class ClientIot():
    def __init__(self, addr=None, token=None):
        # if addr is None or token is None:
        #    addr, token = addressTokenFromConfig(CONFIG_FILE)
        self.addr = addr
        self.token = token
        self.ping()

        self.read_aq = aq_pb2.Sample()

    def ping(self):
        try:
            self._request('GET', '/')
        except ClientError as err:
            if err.http_status_code != requests.codes.forbidden:
                raise err

    def fetch_last_hour(self):

        current_time = round(time.time()*1000)

        # Fetch data for the previous hours. With the Span API this is done by defining start and end times.
        # Values must be in milisecond since epoch.
        # Here, a rough estimate is computed by getting the current time and subtracting 1 hour in miliseconds.

        # TODO: automate for all devices
        resp = self._request('GET',
                               '/collections/17dh0cf43jg007/devices/17dh0cf43jg89l/data',
                               params={"start": current_time-1*60*60*1000,
                                       "end": current_time})

       #  import pdb; pdb.set_trace()

        pm10 = np.zeros(len(resp['data']))
        for i in range(len(resp['data'])):
            # Test with only one value, need to return the average for selected fields
            self.read_aq.ParseFromString(base64.b64decode(resp['data'][i]['payload']))

            pm10[i] = self.read_aq.pm10
        
        return pm10.mean()

    def _request(self, method, path, x=None, params=None):
        json = x and x.json()
        headers = {'X-API-Token': self.token, 'Content-Type': 'application/json'}
        resp = requests.request(method, self.addr + path, json=json, headers=headers, params=params)
        if not resp.ok:
            raise ClientError(resp)
        if method != 'DELETE' and resp.content:
            return resp.json()
