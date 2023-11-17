import pandas as pd
import datetime
import holidays

df = pd.read_csv('bike_rentals.csv')
df['Start_Date'] = pd.to_datetime(df['Start_Date'], format='mixed')

def calculate_price(duration_in_seconds):
    duration_in_minutes = duration_in_seconds / 60 
    periods = -(-duration_in_minutes // 30)  
    return 1.65 * periods

def get_season(date):
    Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
    seasons = {'Spring': (pd.Timestamp(year=Y, month=3, day=21), pd.Timestamp(year=Y, month=6, day=20)),
               'Summer': (pd.Timestamp(year=Y, month=6, day=21), pd.Timestamp(year=Y, month=9, day=20)),
               'Fall': (pd.Timestamp(year=Y, month=9, day=21), pd.Timestamp(year=Y, month=12, day=20)),
               'Winter': (pd.Timestamp(year=Y, month=12, day=21), pd.Timestamp(year=Y, month=3, day=20))}
    date = pd.Timestamp(date).replace(year=Y)
    for season, (season_start, season_end) in seasons.items():
        if season_start <= date <= season_end:
            return season
    return 'Winter'  # Default to winter if not found

def classify_rush_hour(hour):
    if 7 <= hour <= 9:
        return 'Morning Rush'
    elif 16 <= hour <= 19:
        return 'Evening Rush'
    else:
        return 'Off-Peak'

df['Price'] = df['Duration'].apply(calculate_price)
df['Day_Type'] = df['Start_Date'].apply(lambda x: 'Weekend' if x.weekday() > 4 else 'Weekday')
df['Season'] = df['Start_Date'].apply(get_season)

uk_holidays = holidays.UK()

df['Is_Holiday'] = df['Start_Date'].apply(lambda x: x in uk_holidays)
df['Rush_Hour'] = df['Start_Date'].dt.hour.apply(classify_rush_hour)
df['Year'] = df['Start_Date'].dt.year

# Are there broad seasonal patterns in the data 

from statsmodels.tsa.seasonal import seasonal_decompose

df['Month'] = df['Start_Date'].dt.to_period('M')
monthly_data = df.groupby('Month')['Duration'].sum()

# Convert the index to a DatetimeIndex with a monthly frequency
monthly_data.index = monthly_data.index.to_timestamp(freq='M')

# Seasonal Decomposition
result = seasonal_decompose(monthly_data, model='additive')

# Plotting the decomposed components
result.plot()
plt.show()

###### Introducing pricing variation in chosen conditions
# 1. 10 p increase In Evening rush hours

# Original pricing
original_price_per_30_min = 1.65

# Evening rush hour pricing
evening_rush_hour_price_per_30_min = 1.75

# Calculate original revenue for all rentals
df['Original_Price'] = (df['Duration'] / 1800) * original_price_per_30_min

# Calculate new prices, applying the increased price to evening rush hour rentals
df['New_Price'] = df.apply(
    lambda x: (x['Duration'] / 1800) * evening_rush_hour_price_per_30_min 
    if x['Rush_Hour'] == 'Evening Rush' else x['Original_Price'], 
    axis=1
)

# Calculate total original revenue and total new revenue
total_original_revenue = df['Original_Price'].sum()
total_new_revenue = df['New_Price'].sum()

# Calculate the increase in revenue
increase_in_revenue = total_new_revenue - total_original_revenue

print(f"Total original revenue: {total_original_revenue}")
print(f"Total new revenue with increased evening rush hour prices: {total_new_revenue}")
print(f"Increase in revenue: {increase_in_revenue}")

# 2. New seasonal pricing for Summer and Spring
seasonal_price_increase = 1.75

# Calculate original revenue for all rentals
df['Original_Price'] = (df['Duration'] / 1800) * original_price_per_30_min

# Calculate new prices, applying the increased price to Summer and Spring rentals
df['New_Price'] = df.apply(
    lambda x: (x['Duration'] / 1800) * seasonal_price_increase
    if x['Season'] in ['Summer', 'Spring'] else x['Original_Price'],
    axis=1
)

# Calculate total original revenue and total new revenue for Summer and Spring
total_original_revenue_seasons = df[df['Season'].isin(['Summer', 'Spring'])]['Original_Price'].sum()
total_new_revenue_seasons = df[df['Season'].isin(['Summer', 'Spring'])]['New_Price'].sum()

# Calculate the increase in revenue for Summer and Spring
increase_in_revenue_seasons = total_new_revenue_seasons - total_original_revenue_seasons

print(f"Total original revenue for Summer and Spring: {total_original_revenue_seasons}")
print(f"Total new revenue with increased prices for Summer and Spring: {total_new_revenue_seasons}")
print(f"Increase in revenue for Summer and Spring: {increase_in_revenue_seasons}")

# 3. Increased pricing for peak hours during Summer and Spring
peak_price_increase = 1.75

# Calculate original revenue for all rentals
df['Original_Price'] = (df['Duration'] / 1800) * original_price_per_30_min

# Calculate new prices, applying the increased price to peak hours during Summer and Spring
df['New_Price'] = df.apply(
    lambda x: (x['Duration'] / 1800) * peak_price_increase
    if x['Season'] in ['Summer', 'Spring'] and x['Rush_Hour'] in ['Morning Rush', 'Evening Rush'] else x['Original_Price'],
    axis=1
)

# Calculate total original revenue and total new revenue for peak hours during Summer and Spring
total_original_revenue_peak_seasons = df[(df['Season'].isin(['Summer', 'Spring'])) &
                                         (df['Rush_Hour'].isin(['Morning Rush', 'Evening Rush']))]['Original_Price'].sum()
total_new_revenue_peak_seasons = df[(df['Season'].isin(['Summer', 'Spring'])) &
                                    (df['Rush_Hour'].isin(['Morning Rush', 'Evening Rush']))]['New_Price'].sum()

# Calculate the increase in revenue for peak hours during Summer and Spring
increase_in_revenue_peak_seasons = total_new_revenue_peak_seasons - total_original_revenue_peak_seasons

print(f"Total original revenue for peak hours during Summer and Spring: {total_original_revenue_peak_seasons}")
print(f"Total new revenue with increased prices for peak hours during Summer and Spring: {total_new_revenue_peak_seasons}")
print(f"Increase in revenue for peak hours during Summer and Spring: {increase_in_revenue_peak_seasons}")
