import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib
from config import Config
from datetime import datetime, timedelta


class FinancePredictor:
    def __init__(self):
        try:
            self.model = joblib.load(Config.MODEL_PATH)
        except FileNotFoundError:
            self.model = self._train_base_model()
        self.preprocessor = self._create_preprocessor()

    def _train_base_model(self):
        """Создание базовой модели при первом запуске"""
        base_model = RandomForestRegressor(n_estimators=50, random_state=42)
        joblib.dump(base_model, Config.MODEL_PATH)
        return base_model

    def _create_preprocessor(self):
        """Создание препроцессора для категориальных признаков"""
        return ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), ['category'])
            ],
            remainder='passthrough'
        )

    def preprocess_data(self, df: pd.DataFrame):
        df['type'] = df['type'].str.lower().str.strip()
        df['type'] = df['type'].replace({'pacход': 'расход', 'доход': 'доход'})

        df['amount'] = np.where(
            df['type'] == 'доход',
            df['amount'],
            -df['amount']
        )

        df = df.sort_values('date', ascending=True)
        df['date'] = pd.to_datetime(df['date'])

        df['days'] = (df['date'] - df['date'].min()).dt.days
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['month'] = df['date'].dt.month

        for i in range(1, 4):
            df[f'lag_{i}'] = df['amount'].shift(i)

        df['rolling_3'] = df['amount'].rolling(window=3, min_periods=1).mean()
        df = df.dropna()

        feature_columns = ['days', 'day_of_week', 'is_weekend', 'month',
                           'rolling_3', 'lag_1', 'lag_2', 'lag_3']

        X = df[feature_columns]
        y = df['amount']

        return X, y

    def predict_future(self, df: pd.DataFrame, days_ahead: int = 7):
        if len(df) < 3:
            return 0.0

        X, y = self.preprocess_data(df)
        self.model.fit(X, y)

        last_date = df['date'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]

        future_df = pd.DataFrame({
            'days': [(date - last_date).days for date in future_dates],
            'day_of_week': [date.weekday() for date in future_dates],
            'is_weekend': [int(date.weekday() in [5, 6]) for date in future_dates],
            'month': [date.month for date in future_dates],
            'rolling_3': [np.mean(df['amount'].tail(3))] * days_ahead,
            'lag_1': [df['amount'].iloc[-1]] * days_ahead,
            'lag_2': [df['amount'].iloc[-2] if len(df) >= 2 else np.mean(df['amount'])] * days_ahead,
            'lag_3': [df['amount'].iloc[-3] if len(df) >= 3 else np.mean(df['amount'])] * days_ahead
        })

        predictions = self.model.predict(future_df)
        return np.sum(predictions)