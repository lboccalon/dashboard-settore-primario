import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def min_max_scale(values, desired_min, desired_max):
    current_min, current_max = min(values), max(values)
    scaled = (values - current_min) * (desired_max - desired_min) / (
        current_max - current_min
    ) + desired_min
    return scaled


def get_growing_condition(temp: float):
    if temp < -1:
        return "Frost Damage"
    elif temp < 10:
        return "Dormant"
    elif temp < 18:
        return "Growing"
    elif temp < 34:
        return "Optimal"
    elif temp < 41:
        return "Stress"
    else:
        return "Damage"


def generate_environmental_data(start_date, end_date):
    # Generate date range
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    df = pd.DataFrame(index=dates)

    # Day of year for seasonal calculations
    df["day_of_year"] = df.index.dayofyear

    # Temperature generation
    seasonal_temp = 20 + 8 * np.sin(
        2 * np.pi * (df["day_of_year"] - 171) / 365
    )  # Peak in summer
    random_variation = np.random.normal(0, 2, len(df))  # Daily variation
    df["temperature"] = seasonal_temp + random_variation

    # Ensure temperature stays within Anzio ranges
    df["temperature"] = min_max_scale(df["temperature"], 6, 28)

    # Hours of sun (correlated with temperature)
    max_sun_hours = 14  # Summer
    min_sun_hours = 9  # Winter
    seasonal_sun = (max_sun_hours + min_sun_hours) / 2 + (
        max_sun_hours - min_sun_hours
    ) / 2 * np.sin(2 * np.pi * (df["day_of_year"] - 171) / 365)
    df["sun_hours"] = seasonal_sun

    # Rain probability based on seasonal pattern
    rain_prob = 0.22 + 0.16 * np.sin(2 * np.pi * (df["day_of_year"] + 45) / 365)
    rain_events = np.random.random(len(df)) < rain_prob

    # Rain amount based on monthly totals
    base_rain = 61.5 + 46.5 * np.sin(2 * np.pi * (df["day_of_year"] + 45) / 365)
    monthly_days = rain_prob * 30  # approximate days of rain per month
    daily_intensity = base_rain / monthly_days

    df["rain_mm"] = np.where(
        rain_events, np.random.exponential(daily_intensity, len(df)), 0
    )

    # Ensure minimum 1mm for wet days and adjust sun hours
    df.loc[df["rain_mm"] < 1, "rain_mm"] = 0
    df.loc[df["rain_mm"] > 0, "sun_hours"] *= 0.3
    df["sun_hours"] = df["sun_hours"].clip(0, 14)

    # Cloud coverage
    seasonal_cloud = 29 + 17 * np.sin(2 * np.pi * (df["day_of_year"] + 80) / 365)
    cloud_variation = np.random.normal(0, 10, len(df))
    df["cloud_coverage"] = seasonal_cloud + cloud_variation
    df.loc[df["rain_mm"] > 0, "cloud_coverage"] = 100
    df["cloud_coverage"] = df["cloud_coverage"].clip(0, 100)

    # Humidity - influenced by temperature and rain
    base_humidity = 70 - 0.3 * (df["temperature"] - 20)
    rain_effect = np.where(
        df["rain_mm"] > 0,
        15 * (1 - np.exp(-0.1 * df["rain_mm"])),  # Higher rain = higher humidity boost
        0,
    )
    humidity_variation = np.random.normal(0, 3, len(df))
    df["humidity"] = base_humidity + rain_effect + humidity_variation
    df["humidity"] = df["humidity"].clip(40, 95)

    # Growing condition
    df["growing_condition"] = df["temperature"].apply(get_growing_condition)

    # Drop helper column
    df = df.drop("day_of_year", axis=1)

    return df


# Generate 5 years of data
start_date = "2024-01-01"
end_date = "2028-12-31"
data = generate_environmental_data(start_date, end_date)
