import requests


class ClientMet():
    def __init__(self, client_id):
        self.client_id = client_id
        self.endpoint = 'https://frost.met.no/observations/v0.jsonld'

    def fetch_last_data(self, source, elements, mask=None):

        # Define endpoint and parameters
        params = {
            'sources': source,
            'elements': ','.join(elements),
            'referencetime': 'latest',
            'timeresolutions': 'PT1H',
        }

        data = self._request(params)

        out_data = dict.fromkeys(elements)

        for x in data[0]['observations']:
            out_data[x['elementId']] = x['value']

            # If any of the elements is None, it means that there is missing data and we throw an Exception
        if None in out_data.values():
            raise ValueError("Missing data for MET sensor " + source)

        if mask is None:
            pass
        elif len(mask) != len(elements):
            print('Size of mask different from elements, ignoring')
        else:
            for i in range(len(elements)):
                out_data[mask[i]] = out_data.pop(elements[i])

        return out_data

    def _request(self, params):
        # Issue an HTTP GET request
        r = requests.get(self.endpoint, params, auth=(self.client_id, ''))
        # Extract JSON data
        json = r.json()

        # Check if the request worked, print out any errors
        if r.status_code == 200:
            data = json['data']
        else:
            print('Error! Returned status code %s' % r.status_code)
            print('Message: %s' % json['error']['message'])
            print('Reason: %s' % json['error']['reason'])

        return data
