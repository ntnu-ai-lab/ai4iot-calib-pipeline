from api_clients.client_iot import ClientIot
from api_clients.client_nilu import ClientNilu
from api_clients.client_met import ClientMet


class DataSourceManager():
    def __init__(self, config):
        self.config = config
        # Create api clients
        self.client_iot = ClientIot(addr=config['iot_api'],
                                    token=config['iot_token'])
        self.client_met = ClientMet(client_id=config['met_id'])
        self.client_nilu = ClientNilu()

    def collect_sample(self):
        # Device is hardcoded for Elgeseter
        iot_data = self.client_iot.fetch_last_data(device='17dh0cf43jg89l',
                                                   elements=['pm1','pm25','pm10','opc_temp','opc_hum'],
                                                   mask=['pm1_iot','pm25_iot','pm10_iot','temp_iot','hum_iot'])

        nilu_data = self.client_nilu.fetch_last_data(station='Elgeseter',
                                                     elements=['pm2.5', 'pm10'],
                                                     mask=['pm25_nilu', 'pm10_nilu'])

        # Hardcoded: only fetch data from Voll station
        met_data = self.client_met.fetch_last_data(source='SN68860',
                                                   elements=['air_temperature', 'relative_humidity', 'sum(precipitation_amount PT1H)', 'surface_air_pressure', 'wind_speed', 'wind_from_direction'],
                                                   mask=['temperature', 'humidity', 'precipitation', 'air_pressure', 'wind_speed', 'wind_direction'])

        return {**iot_data, **met_data, **nilu_data}
