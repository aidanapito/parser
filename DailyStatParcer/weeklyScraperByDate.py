import pandas as pd
import glob
from datetime import datetime, timedelta

# Assuming you have seven daily CSV files in the same directory
daily_files = glob.glob('./CSVs/daily_stats_*.csv')  # Adjust the file pattern as needed

# Create an empty DataFrame to store the accumulated data
accumulated_df = pd.DataFrame()

# Loop through the daily files
for daily_file in daily_files:
    df = pd.read_csv(daily_file)

    # Assuming you have a 'Week' column in your CSV indicating the week number
    # You can group by 'Player' and 'Week', then sum up the stats for each player for each week
    grouped_df = df.groupby(['Player', 'Week']).sum().reset_index()

    # Add the grouped data to the accumulated DataFrame
    accumulated_df = accumulated_df.append(grouped_df, ignore_index=True)

# Get the beginning of the week's date
beginning_of_week = (datetime.now() - timedelta(days=datetime.now().weekday())).date()

# Save the accumulated data to a new CSV file with the week's date in the name
weekly_totals_csv = f'weekly_totals_week_of_{beginning_of_week}.csv'
accumulated_df.to_csv(weekly_totals_csv, index=False)

print(f'Weekly totals combined and saved to {weekly_totals_csv}')