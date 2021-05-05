import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve
import datetime

class ClassifierManager():
    model = None

    def train(self,params):
        #User options
        use_temporal_features = params['use_temporal']
        use_delta_features = params['use_delta']
        use_forecast_features = params['use_forecast']
        use_only_pm = params['use_only_pm']
        use_weather = params['use_weather']
        if use_weather == False: use_forecast_features = False
        use_traffic = params['use_traffic']

        station=params['station']
        pollutant=params['pollutant']
        threshold=params['threshold']
        #####
        
        df = pd.read_csv("data/trondheim_data.csv", low_memory=False)

        df = df.set_index(pd.to_datetime(df['datetime'],utc=True))

        # # Add the max PM25 value for the next 24 hours

        n = 24
        indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=n)
        df[station+"_"+pollutant+"_24hour_rolling_max"] = df[station+"_"+pollutant].rolling(window=indexer, min_periods=1).max()
        
        # # Create pollution indicator for threshold mikrogram pr m3 threshold 
        
        df["pollution_indicator_max"] = 1.0*(df[station+"_"+pollutant+"_24hour_rolling_max"] >= threshold)
        df['pollution_indicator_max'] = df['pollution_indicator_max'].fillna(0).astype(np.int64)

        # # Remove datetime column as it is a string and the
        # # RF classifier deals only with columns of nummeric values
        df = df.drop(['datetime'], axis=1)

        # Need to drop the rolling max feature (contains the information of the class label) in order to avoid a perfect classification score 
        df = df.drop([station+"_"+pollutant+"_24hour_rolling_max"], axis=1)

        ##Set up features
        #Bakke Kirke is no longer available, cannot use in a deployment scenario
        df = df.drop(['bakke_kirke_pm10','bakke_kirke_pm2.5','bakke_kirke_no','bakke_kirke_no2','bakke_kirke_nox'],axis=1)
        
        # 6 temporal features
        if use_temporal_features == True:
            df['hour_of_day'] = df.index.hour + 1
            df['month_of_year'] = df.index.month
            df['day_of_week'] = df.index.dayofweek
            df['day_of_month'] = df.index.day
            df['day_of_year'] = df.index.dayofyear
            df['season'] = (df.index.month%12 + 3)//3
            
        if use_weather == False:
            df = df.drop(['air_temperature','wind_speed','precipitation','relative_humidity','air_pressure','wind_direction'], axis=1)
    
        if use_only_pm == True:
            df = df.drop(['e6-tiller_no','e6-tiller_nox','e6-tiller_no2','elgeseter_no','elgeseter_no2','elgeseter_nox','torvet_no2'], axis=1)

        # 15 delta features, i.e. trend/change for the past 24 hours
        if use_delta_features == True:
            df['delta_e6-tiller_pm10'] = df['e6-tiller_pm10'] - df['e6-tiller_pm10'].shift(periods=24)
            df['delta_e6-tiller_pm2.5'] = df['e6-tiller_pm10'] - df['e6-tiller_pm2.5'].shift(periods=24)
            df['delta_elgeseter_pm10'] = df['elgeseter_pm10'] - df['elgeseter_pm10'].shift(periods=24)
            df['delta_elgeseter_pm2.5'] = df['elgeseter_pm2.5'] - df['elgeseter_pm2.5'].shift(periods=24)
            df['delta_torvet_pm10'] = df['torvet_pm10'] - df['torvet_pm10'].shift(periods=24)
            df['delta_torvet_pm2.5'] = df['torvet_pm2.5'] - df['torvet_pm2.5'].shift(periods=24)
            df['delta_elgeseter_bru_below_5.6m'] = df['elgeseter_bru_below_5.6m'] - df['elgeseter_bru_below_5.6m'].shift(periods=24)
            df['delta_elgeseter_bru_above_5.6m'] = df['elgeseter_bru_above_5.6m'] - df['elgeseter_bru_above_5.6m'].shift(periods=24)
    
            if use_only_pm == False:
                df['delta_e6-tiller_no2'] = df['e6-tiller_no2'] - df['e6-tiller_no2'].shift(periods=24)
                df['delta_elgeseter_no2'] = df['elgeseter_no2'] - df['elgeseter_no2'].shift(periods=24)
                df['delta_torvet_no2'] = df['torvet_no2'] - df['torvet_no2'].shift(periods=24)
            
            if use_weather == True:
                df['delta_air_temperature'] = df['air_temperature'] - df['air_temperature'].shift(periods=24)
                df['delta_wind_speed'] = df['wind_speed'] - df['wind_speed'].shift(periods=24)
                df['delta_precipitation'] = df['precipitation'] - df['precipitation'].shift(periods=24)
                df['delta_relative_humidity'] = df['relative_humidity'] - df['relative_humidity'].shift(periods=24)
                df['delta_air_pressure'] = df['air_pressure'] - df['air_pressure'].shift(periods=24)
        
        # 5 forecast features, i.e. a perfect one using the actual values for weather measurements 24 hours ahead 
        if use_forecast_features == True:
            df["forecast_air_temperature"] = df['air_temperature'].shift(periods=-24)
            df["forecast_wind_speed"] = df['wind_speed'].shift(periods=-24)
            df["forecast_precipitation"] = df['precipitation'].shift(periods=-24)
            df["forecast_relative_humidity"] = df['relative_humidity'].shift(periods=-24)
            df["forecast_air_pressure"] = df['air_pressure'].shift(periods=-24)

        if use_traffic == False:
            df = df.drop(['innherredsveien_below_5.6m','innherredsveien_above_5.6m','elgeseter_bru_below_5.6m','elgeseter_bru_above_5.6m','e6_below_5.6m','e6_above_5.6m'],axis=1)
    
        ##For now assume that cleaning actions do not make much of a difference (to make it easy to use model in a pipeline)
        df = df.drop(['sweeping','mgcl2'],axis=1)


        # Set random seed to ensure reproducible runs
        RSEED = 50
        
        # Extract the labels
        labels = np.array(df.pop('pollution_indicator_max'))

        # 30% examples in test data
        train, test, train_labels, test_labels = train_test_split(df, labels, 
                                                          stratify = labels,
                                                          test_size = 0.3, 
                                                          random_state = RSEED)

        train = train.fillna(train.mean())
        test = test.fillna(train.mean())

        # Create the model with 100 trees
        self.model = RandomForestClassifier(n_estimators=100, 
                               random_state=RSEED, 
                               max_features = 'sqrt',
                               n_jobs=-1, verbose = 1)

        # Fit on training data
        self.model.fit(train, train_labels)

        test_predictions = self.model.predict(test)
        results = {}
        test_probs = self.model.predict_proba(test)[:, 1]
        results['recall'] = recall_score(test_labels, test_predictions)
        results['precision'] = precision_score(test_labels, test_predictions)
        results['roc'] = roc_auc_score(test_labels, test_probs)

        # train_predictions = model.predict(train)
        # train_probs = model.predict_proba(train)[:, 1]
        # train_results = {}
        # train_results['recall'] = recall_score(train_labels, train_predictions)
        # train_results['precision'] = precision_score(train_labels, train_predictions)
        # train_results['roc'] = roc_auc_score(train_labels, train_probs)

        return results
        
    def predict(self,sample):

        predicted_aq = self.model.predict([[sample['e6_tiller_pm10'],
                             sample['e6_tiller_pm25'],
                             sample['elgeseter_pm10'],
                             sample['elgeseter_pm25'],
                             sample['torvet_pm10'],
                             sample['torvet_pm25']]])

        return predicted_aq
