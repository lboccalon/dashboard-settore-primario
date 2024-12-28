import pandas as pd
import numpy as np


def min_max_scale(values, desired_min, desired_max):
    current_min, current_max = min(values), max(values)
    scaled = (values - current_min) * (desired_max - desired_min) / (
        current_max - current_min
    ) + desired_min
    return scaled


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
    df["temperature"] = df["temperature"].round(1)

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
    df["rain_mm"] = df["rain_mm"].round()
    df["sun_hours"] = df["sun_hours"].clip(0, 14)
    df["sun_hours"] = df["sun_hours"].round(2)

    # Cloud coverage
    seasonal_cloud = 29 + 17 * np.sin(2 * np.pi * (df["day_of_year"] + 80) / 365)
    cloud_variation = np.random.normal(0, 10, len(df))
    df["cloud_coverage"] = seasonal_cloud + cloud_variation
    df.loc[df["rain_mm"] > 0, "cloud_coverage"] = 100
    df["cloud_coverage"] = df["cloud_coverage"].clip(0, 100)
    df["cloud_coverage"] = df["cloud_coverage"].round()

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
    df["humidity"] = df["humidity"].round()

    # Drop helper column
    df = df.drop("day_of_year", axis=1)

    return df


def simulate_vineyard_yield(data: pd.DataFrame, field_size_hectares: int = 100):
    # Filter data for the last year
    last_year = data.loc[data.index >= data.index[-1] - pd.DateOffset(years=1)]

    # Define baseline yield per hectare (kg)
    baseline_yield_per_hectare = np.random.randint(8000, 12000)  # 8,000-12,000 kg
    baseline_yield_total = baseline_yield_per_hectare * field_size_hectares

    # Aggregate environmental factors
    avg_temperature = last_year["temperature"].mean()
    avg_rainfall = last_year["rain_mm"].sum()
    avg_sun_hours = last_year["sun_hours"].mean()
    avg_humidity = last_year["humidity"].mean()

    # Factor adjustments
    # Temperature: Optimal range 18°C to 28°C
    temp_factor = 1.0
    if avg_temperature < 18:
        temp_factor -= (18 - avg_temperature) * 0.05  # 5% penalty per °C below optimal
    elif avg_temperature > 28:
        temp_factor -= (avg_temperature - 28) * 0.05  # 5% penalty per °C above optimal

    # Rainfall: Optimal annual total ~600mm-800mm
    rain_factor = 1.0
    if avg_rainfall < 600:
        rain_factor -= (600 - avg_rainfall) * 0.001  # 0.1% penalty per mm below
    elif avg_rainfall > 800:
        rain_factor -= (avg_rainfall - 800) * 0.001  # 0.1% penalty per mm above

    # Sunlight: Optimal average 12 hours/day
    sun_factor = min(avg_sun_hours / 12, 1.0)  # Cap at 1.0

    # Humidity: High humidity reduces yield
    humidity_factor = 1.0
    if avg_humidity > 80:
        humidity_factor -= (avg_humidity - 80) * 0.01  # 1% penalty per unit above 80

    # Compute total adjustment factor
    adjustment_factor = temp_factor * rain_factor * sun_factor * humidity_factor

    # Adjust the baseline yield
    adjusted_yield = baseline_yield_total * adjustment_factor

    return {
        "baseline_yield_kg": baseline_yield_total,
        "adjusted_yield_kg": adjusted_yield,
        "adjustment_factor": adjustment_factor,
        "avg_temperature": avg_temperature,
        "avg_rainfall_mm": avg_rainfall,
        "avg_sun_hours": avg_sun_hours,
        "avg_humidity": avg_humidity,
    }


# Generate 5 years of data
start_date = "2024-01-01"
end_date = "2028-12-31"
data = generate_environmental_data(start_date, end_date)


