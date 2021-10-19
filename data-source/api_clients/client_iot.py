import time
import requests

from . import aq_pb2
import base64

import numpy as np

from google.protobuf.json_format import MessageToDict


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
        self.addr = 'https://api.lab5e.com/span'
        self.token = token
        self.ping()

        self.read_aq = aq_pb2.Sample()

    def ping(self):
        try:
            self._request('GET', '/')
        except ClientError as err:
            if err.http_status_code != requests.codes.forbidden:
                raise err

    def fetch_last_data(self, device, elements, mask=None):

        current_time = round(time.time() * 1000)

        end_time = current_time - (current_time % (3600 * 1000))
        start_time = end_time - 1 * 60 * 60 * 1000

        # Fetch data for the previous hours. With the Span API this is done by defining start and end times.
        # Values must be in milisecond since epoch.
        # Here, a rough estimate is computed by getting the current time and subtracting 1 hour in miliseconds.

        resp = self._request('GET',
                               '/collections/17dh0cf43jg007/devices/{0}/data'.format(device),
                               params={"start": start_time,
                                       "end": end_time})

        data = {}
        for el in elements:
            data[el] = np.zeros(len(resp['data']))

        for i in range(len(resp['data'])):
            self.read_aq.ParseFromString(base64.b64decode(resp['data'][i]['payload']))
            msg = MessageToDict(self.read_aq, preserving_proto_field_name=True)

            for el in elements:
                data[el][i] = msg[el]

        out_data = {}
        for el in elements:
            # out_data = out_data + (data[el].mean(),)
            out_data[el] = data[el].mean()

        if mask is None:
            pass
        elif len(mask) != len(elements):
            print('Size of mask different from elements, ignoring')
        else:
            for i in range(len(elements)):
                out_data[mask[i]] = out_data.pop(elements[i])

        return out_data

    def _request(self, method, path, x=None, params=None):
        json = x and x.json()
        headers = {'X-API-Token': self.token, 'Content-Type': 'application/json'}
        resp = requests.request(method, self.addr + path, json=json, headers=headers, params=params)
        if not resp.ok:
            raise ClientError(resp)
        if method != 'DELETE' and resp.content:
            return resp.json()
