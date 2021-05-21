import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score as r2
import math


class CalibrationManager():
    model = None

    def fill_holes(self, df, method, zero_streak):
        """ This is where we deal with nans and suspicious strings of zeros """
        # reconsider what columns to drop/fill
        columns = df.columns
        for col in columns:
            zeros = 0
            for indx, val in df[col].items():
                if val != val or val == 0:
                    zeros += 1
                else:
                    zeros = 0
                if zeros == zero_streak:
                    for i in range(zero_streak):
                        if method == 'mean':
                            df[col].at[indx - pd.Timedelta(hours=i)] = df[col].mean()
                        elif method == 'mean_for_hour':
                            df[col].at[indx - pd.Timedelta(hours=i)] = df[df.index.hour == (indx.hour - i) % 24][
                                col].mean()
                        elif method == 'mean_for_hour_week' or (method == 'remove' and (not '_nilu' in col)):
                            df[col].at[indx - pd.Timedelta(hours=i)] = df[(df.index.hour == (indx.hour - i) % 24) &
                                                                          (indx.dayofweek == df.index.dayofweek)][
                                col].mean()
                        elif method == 'remove' and '_nilu' in col:
                            if indx in df.index:
                                df = df.drop([indx])
                elif zeros > zero_streak:
                    if method == 'mean':
                        df[col].at[indx] = df[col].mean()
                    elif method == 'mean_for_hour':
                        df[col].at[indx] = df[df.index.hour == indx.hour][col].mean()
                    elif method == 'mean_for_hour_week' or (method == 'remove' and (not '_nilu' in col)):
                        df[col].at[indx] = \
                            df[(df.index.hour == indx.hour) & (indx.dayofweek == df.index.dayofweek)][col].mean()
                    elif method == 'remove' and '_nilu' in col and not '_stratum_' in col:
                        if indx in df.index:
                            df = df.drop([indx])
                if val != val:
                    if method == 'mean':
                        df[col].at[indx] = df[col].mean()
                    elif method == 'mean_for_hour':
                        df[col].at[indx] = df[df.index.hour == indx.hour][col].mean()
                    elif method == 'mean_for_hour_week' or method == 'remove':
                        df[col].at[indx] = \
                            df[(df.index.hour == indx.hour) & (indx.dayofweek == df.index.dayofweek)][col].mean()
        return df

    def train(self, params):
        # station used for training
        station = params['station']
        # pollutant to predict
        pollutant = params['pollutant']

        if station == 'elgeseter':
            other_station = 'torget'
        else:
            other_station = 'elgeseter'
        if pollutant == 'pm10':
            other_pollutant = 'pm25'
        else:
            other_pollutant = 'pm10'

        # how to handle NaN's and suspiciously long strings of 0s
        fill_method = 'remove'  # 'mean_for_hour', 'mean', 'mean_for_hour_week', 'remove'
        # how long of a streak of 0s is suspicious?
        zero_streak = 12

        # some training options
        test_size = 0.25
        # divisor for max features (max_feat_div = x => max features will be floor(1/x) of total features, or 1)
        max_feat_div = 3
        # max depth of trees, to minimize overfitting
        depth = 10
        # number of trees in random forest
        trees = 500

        # I will slice the original dataframe and adjust it, triggering a warning that the adjustment does not happen
        # in the original dataframe. I don't care about that; this silences that warning.
        pd.options.mode.chained_assignment = None  # default='warn'

        data1 = "data/dump_with_all_features-til23_02-utc.csv"
        # the last 20ish % of data2 is messy
        data2 = "data/dump_with_all_features_til26-03.csv"
        df = pd.read_csv(data1, low_memory=False)
        df = df.set_index(pd.to_datetime(df['time'], utc=True))
        df = df.drop(columns=['time'])

        # replacing wind_direction with sine and cosine
        df['wind_direction_sin'] = np.sin(df['wind_direction'] * np.pi / 180)
        df['wind_direction_cos'] = np.cos(df['wind_direction'] * np.pi / 180)
        df = df.drop(columns=['wind_direction'])
        # adding helpful time variables
        df['hour_sin'] = np.sin(df.index.hour * 2 * np.pi / 24)
        df['hour_cos'] = np.cos(df.index.hour * 2 * np.pi / 24)
        df['day_of_week_sin'] = np.sin(df.index.dayofweek * 2 * np.pi / 7)
        df['day_of_week_cos'] = np.cos(df.index.dayofweek * 2 * np.pi / 7)
        df['day_of_year_sin'] = np.sin(df.index.dayofyear * 2 * np.pi / 365)
        df['day_of_year_cos'] = np.cos(df.index.dayofyear * 2 * np.pi / 365)

        # creating separate dataframes for each station
        df_other = df
        df = df.loc[:, ~df.columns.str.contains(other_station)]
        df_other = df_other.loc[:, ~df_other.columns.str.contains(station)]

        print("Patching data..")
        df = self.fill_holes(df, fill_method, zero_streak)
        df_other = self.fill_holes(df_other, fill_method, zero_streak)

        # making a combined station target dataframe, removing all nilu data from df
        # this must be done after fill_holes(), as holes in nilu data are patched there
        target = df[[col for col in df.columns if pollutant + '_nilu' in col]]
        df = df.loc[:, ~df.columns.str.contains('_nilu')]
        target_other = df_other[[col for col in df_other.columns if pollutant + '_nilu' in col]]
        df_other = df_other.loc[:, ~df_other.columns.str.contains('_nilu')]
        # creating separate targets for each station

        train, test = np.split(df, [int((1 - test_size) * len(df))])
        train_target, test_target = np.split(target, [int((1 - test_size) * len(target))])

        # size of random pool of features per tree, helps create a more balanced feature importance
        max_feat = int(len(train.columns) / max_feat_div)
        if max_feat == 0:
            max_feat = 1

        print("Training..")
        train_target = train_target.squeeze()
        self.model = RandomForestRegressor(n_estimators=trees, max_depth=depth, max_features=max_feat)
        self.model.fit(train, train_target)
        result_train = train_target.to_frame()

        predictions_train = self.model.predict(train)
        result_train = result_train.rename(columns={result_train.columns[0]: 'target'})
        result_train['prediction'] = predictions_train
        ms_error_train = mse(result_train['target'], result_train['prediction'])
        rmse_train = math.sqrt(ms_error_train)
        r2_train = r2(result_train['target'], result_train['prediction'])

        predictions_test = self.model.predict(test)
        result_test = test_target  # .to_frame()
        result_test = result_test.rename(columns={result_test.columns[0]: 'target'})
        result_test['prediction'] = predictions_test
        ms_error_test = mse(result_test['target'], result_test['prediction'])
        rmse_test = math.sqrt(ms_error_test)
        r2_test = r2(result_test['target'], result_test['prediction'])

        start_cut = 0
        end_cut = 1
        df_other = df_other[int(start_cut * len(df_other)): int(end_cut * len(df_other))]
        predictions_other = self.model.predict(df_other)
        result_other = target_other
        result_other = result_other[int(start_cut * len(result_other)): int(end_cut * len(result_other))]
        result_other = result_other.rename(columns={result_other.columns[0]: 'target'})
        result_other['prediction'] = predictions_other
        ms_error_other = mse(result_other['target'], result_other['prediction'])
        rmse_other = math.sqrt(ms_error_other)
        r2_other = r2(result_other['target'], result_other['prediction'])

        results = {'rmse': rmse_test}
        return results

    def predict(self):

        return


if __name__ == '__main__':
    train_params = {'station': 'elgeseter',
                    'pollutant': 'pm25'}
    calibration_manager = CalibrationManager()
    rmse_test = calibration_manager.train(train_params)
    print(rmse_test)


