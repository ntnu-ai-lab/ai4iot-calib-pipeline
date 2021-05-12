from calibration_manager import CalibrationManager

manager = CalibrationManager()
params = {'train_sensor' : 'elgeseter', 'pollutant' : 'pm10'}
print(manager.train(params))
