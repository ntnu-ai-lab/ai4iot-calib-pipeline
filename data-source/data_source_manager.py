from api_clients.client_iot import ClientIot
from api_clients.client_nilu import ClientNilu
from api_clients.client_met import ClientMet


class DataSourceManager():
    def __init__(self, config, iot_sensors, nilu_sensors):

        self.config = config
        
        # Create api clients
        self.client_iot = ClientIot(token=config['iot_token'])
        self.client_met = ClientMet(client_id=config['met_id'])
        self.client_nilu = ClientNilu()

        self.iot_sensors = iot_sensors
        self.nilu_sensors = nilu_sensors

    def collect_sample(self):
        # Generalize to read from iot_sensors input
        iot_data = dict.fromkeys(self.iot_sensors.keys())

        nilu_data = dict.fromkeys(self.nilu_sensors)

        met_data = {}

        try:
            for sensor in self.iot_sensors:
                iot_data[sensor] = self.client_iot.fetch_last_data(device=self.iot_sensors[sensor], elements=['pm1', 'pm25', 'pm10', 'opc_temp', 'opc_hum'],
                                                                   mask=['pm1_iot', 'pm25_iot', 'pm10_iot', 'temp_iot', 'hum_iot'])

            for sensor in self.nilu_sensors:
                nilu_data[sensor] = self.client_nilu.fetch_last_data(station=sensor,
                                                             elements=['pm2.5', 'pm10'],
                                                             mask=['pm25_nilu', 'pm10_nilu'])

            # Hardcoded: for now only fetch data from Voll station
            met_data = self.client_met.fetch_last_data(source='SN68860',
                                                       elements=['air_temperature', 'relative_humidity', 'sum(precipitation_amount PT1H)', 'surface_air_pressure', 'wind_speed', 'wind_from_direction'],
                                                       mask=['temperature', 'humidity', 'precipitation', 'air_pressure', 'wind_speed', 'wind_direction'])

        except ValueError as e:
            raise ValueError(e)

        return iot_data, met_data, nilu_data
