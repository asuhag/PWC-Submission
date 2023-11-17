import pandas as pd
import datetime
import holidays
import seaborn as sns 
import matplotlib.pyplot as plt 

df = pd.read_csv('bike_rentals.csv')
print(df['Duration'].describe())
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
df['Hour_Rounded'] = df['Start_Date'].dt.hour

# Convert 'Duration' to days for total calculation
df['Duration_Days'] = df['Duration'] / 86400

# Calculate total duration in days by year
total_duration_days_year = df.groupby('Year')['Duration_Days'].sum().reset_index()

# Plotting total duration in days by year
plt.figure(figsize=(10, 6))
sns.barplot(x='Year', y='Duration_Days', data=total_duration_days_year)
plt.title('Total Duration by Year (in Days)')
plt.ylabel('Total Duration (in Days)')
plt.xlabel('Year')
plt.show()

# Function to create bar plots for various categories
def category_bar_plot(category):
    plt.figure(figsize=(10, 6))
    sns.countplot(x=category, data=df)
    plt.title(f'Number of Hires by {category}')
    plt.ylabel('Number of Hires')
    plt.xlabel(category)
    plt.show()

# Plot 3: Bar plots for various categories
categories = ['Day_Type', 'Is_Holiday', 'Season', 'Rush_Hour', 'Hour_Rounded']
for category in categories:
    category_bar_plot(category)

# Count rentals in each category
category_counts = df['Rush_Hour'].value_counts()

# Normalize by number of hours in each category
category_counts['Morning Rush'] /= 2  # 2 hours in the morning rush
category_counts['Evening Rush'] /= 3  # 3 hours in the evening rush
category_counts['Off-Peak'] /= 19     # 19 hours off-peak

# Plot the normalized counts
sns.barplot(x=category_counts.index, y=category_counts.values)
plt.title('Normalized Bike Rentals per Hour by Time of Day')
plt.ylabel('Rentals per Hour')
plt.xlabel('Time of Day Category')
plt.show()


# Total earnings for each Rush_Hour category
total_earnings_rush_hour = df.groupby('Rush_Hour')['Price'].sum()

# Total earnings for each Season
total_earnings_season = df.groupby('Season')['Price'].sum()

# Total earnings for each Day_Type
total_earnings_day_type = df.groupby('Day_Type')['Price'].sum()

# Total earnings overall
total_earnings = df['Price'].sum()

# Compute fractions
fraction_earnings_rush_hour = total_earnings_rush_hour / total_earnings
fraction_earnings_season = total_earnings_season / total_earnings
fraction_earnings_day_type = total_earnings_day_type / total_earnings

# Rush_Hour
sns.barplot(x=fraction_earnings_rush_hour.index, y=fraction_earnings_rush_hour.values)
plt.title('Fraction of Total Earnings by Rush Hour Category')
plt.ylabel('Fraction of Total Earnings')
plt.xlabel('Rush Hour Category')
plt.show()

# Seasons
sns.barplot(x=fraction_earnings_season.index, y=fraction_earnings_season.values)
plt.title('Fraction of Total Earnings by Season')
plt.ylabel('Fraction of Total Earnings')
plt.xlabel('Season')
plt.show()

# Day_Type
sns.barplot(x=fraction_earnings_day_type.index, y=fraction_earnings_day_type.values)
plt.title('Fraction of Total Earnings by Day Type')
plt.ylabel('Fraction of Total Earnings')
plt.xlabel('Day Type')
plt.show()

# Histogram of rentals by hour on weekdays and weekends 

hourly_counts = df.groupby([df['Start_Date'].dt.hour, 'Day_Type']).size().reset_index(name='Hires')

# Create a count plot
plt.figure(figsize=(14, 7))
sns.barplot(data=hourly_counts, x='Start_Date', y='Hires', hue='Day_Type', palette='coolwarm')
plt.title('Count of Bike Rentals by Hour and Day Type')
plt.xlabel('Hour of the Day')
plt.ylabel('Count of Rentals')
plt.legend(title='Day Type')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Normalised hires on weekdays and weekends

# Count the total hires for weekdays and weekends
total_hires_by_day_type = df.groupby('Day_Type').size().reset_index(name='Total_Hires')

# Calculate the number of weekdays and weekends
num_weekdays = df[df['Day_Type'] == 'Weekday']['Start_Date'].dt.date.nunique()
num_weekends = df[df['Day_Type'] == 'Weekend']['Start_Date'].dt.date.nunique()

# Normalize the total hires by the number of days
total_hires_by_day_type['Normalized_Hires'] = total_hires_by_day_type.apply(
    lambda x: x['Total_Hires'] / num_weekdays if x['Day_Type'] == 'Weekday' else x['Total_Hires'] / num_weekends, axis=1)

# Create a bar plot
plt.figure(figsize=(8, 6))
sns.barplot(data=total_hires_by_day_type, x='Day_Type', y='Normalized_Hires', palette='Set2')
plt.title('Normalized Total Hires on Weekdays and Weekends')
plt.xlabel('Day Type')
plt.ylabel('Normalized Total Hires')
plt.show()
