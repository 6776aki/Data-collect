import pandas as pd
from collections import defaultdict
# Load data and parse timestamps
df = pd.read_csv('2025-01-22_WIFUSDT_1m_data.csv', parse_dates=['Open Time'])

# Resample to 1-hour intervals and sum volume
hourly_df = df.resample('1H', on='Open Time')['Volume'].sum().reset_index()
hourly_df['Date'] = hourly_df['Open Time'].dt.date
hourly_df['Hour'] = hourly_df['Open Time'].dt.hour

# Find peak 2-hour window for each day
results = []
for date, group in hourly_df.groupby('Date'):
    max_volume = 0
    best_start = None
    best_end = None
    
    # Check all consecutive hour pairs (same day only)
    for i in range(len(group)-1):
        current_hour = group.iloc[i]
        next_hour = group.iloc[i+1]
        
        # Verify hours are consecutive and same day
        if current_hour['Hour'] + 1 == next_hour['Hour']:
            total_volume = current_hour['Volume'] + next_hour['Volume']
            
            if total_volume > max_volume:
                max_volume = total_volume
                best_start = current_hour['Open Time']
                best_end = next_hour['Open Time'] + pd.Timedelta(hours=1)

    # Format results if valid period found
    if best_start:
        start_str = best_start.strftime("%I.00%p").lstrip('0').lower()
        end_str = best_end.strftime("%I.00%p").lstrip('0').lower()
        results.append(f"{date} most traded time period is --> {start_str} - {end_str}")
        
for result in results:
    print(result)
# Print results
period_counts = defaultdict(int)

for result in results:
    # Extract just the time period portion
    period = result.split("--> ")[1].strip()
    period_counts[period] += 1

# Find the most common period(s)
max_count = max(period_counts.values())
common_periods = [period for period, count in period_counts.items() if count == max_count]

# Generate final output
print("\nMost Common Trading Periods Across All Dates:")
for period in common_periods:
    print(f"{period} (Occurred {max_count} days)")
    print("Best Time to Trade: " + period.split(" - ")[0].replace(".00", "") + " to " + 
          period.split(" - ")[1].replace(".00", ""))

# Optional: Show full distribution
print("\nFull Time Period Distribution:")
for period, count in sorted(period_counts.items()):
    print(f"{period}: {count} days")