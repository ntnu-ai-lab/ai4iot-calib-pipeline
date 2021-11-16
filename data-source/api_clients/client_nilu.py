import pandas as pd


class ClientNilu():
    def __init__(self):
        self.url = 'https://api.nilu.no/aq/utd?areas=trondheim&components='

    def fetch_last_data(self, station, elements, mask=None):
        # Safety check because of different naming standards between NILU API and others
        if station == 'Torget':
            station = 'Torvet'

        url = self.url
        for el in elements:
            url = url + el + ';'

        data = pd.DataFrame.from_records(pd.read_json(url))[['station', 'component', 'toTime', 'value', 'index']]

        # If there is missing data we raise an exception as calibration module cannot handle it

        if station not in data['station'].unique():
            raise ValueError("Missing data for NILU station " + station)

        out_data = {}
        for el in elements:
            # If station data is not in API response, there is missing data and we throw an exception
            if station not in data[data['component'] == el.upper()]['station'].unique():
                raise ValueError("Missing data for NILU station " + station)

            out_data[el] = data.loc[(data['station'] == station) & (data['component'] == el.upper()), 'value'].iloc[0]

        if mask is None:
            pass
        elif len(mask) != len(elements):
            print('Size of mask different from elements, ignoring')
        else:
            for i in range(len(elements)):
                out_data[mask[i]] = out_data.pop(elements[i])

        return out_data
