import joblib


class CalibrationManager():
    def __init__(self):
        ## TODO: Change to path for docker container, chanegd temporarily for testing
        self.model_pm25 = joblib.load('../data/model_elgeseter_pm25.pkl')
        self.model_pm10 = joblib.load('../data/model_elgeseter_pm10.pkl')

    def predict(self, sample):
        calibrated_pm25 = self.model_pm25.predict(sample)
        calibrated_pm10 = self.model_pm10.predict(sample)

        return calibrated_pm25, calibrated_pm10
