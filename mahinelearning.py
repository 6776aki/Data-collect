import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load data
df = pd.read_csv('2025-01-22_WIFUSDT_1m_data.csv', parse_dates=['Open Time'])

# Feature Engineering
df['Hour'] = df['Open Time'].dt.hour
df['Minute'] = df['Open Time'].dt.minute
df['DayOfWeek'] = df['Open Time'].dt.dayofweek

# Target Variable: Trading Volume
y = df['Volume']

# Features
features = ['Hour', 'Minute', 'DayOfWeek']
X = df[features]

# Handle infinite and NaN values
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.dropna(inplace=True)
y = y[X.index]  # Align target with cleaned features

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Feature importance
feature_importances = pd.Series(model.feature_importances_, index=features)
print("\nFeature Importances:")
print(feature_importances.sort_values(ascending=False))

# Predict the busiest hours
busiest_hours = df.groupby('Hour')['Volume'].mean().sort_values(ascending=False)
print("\nBusiest Hours to Trade (Based on Trading Volume):")
print(busiest_hours)