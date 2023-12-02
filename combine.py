import pandas as pd
import subprocess
import time

startTime = time.time()

def rename_columns(df, suffix):
    return df.rename(columns={col: f'{col}_{suffix}' for col in df.columns})

#run files
subprocess.run(['python', 'GroupAParser.py'])
subprocess.run(['python', 'GroupAV2Parser.py'])
subprocess.run(['python', 'GroupAV3Parser.py'])
subprocess.run(['python', 'GroupBParser.py'])
subprocess.run(['python', 'GroupBV2Parser.py'])
subprocess.run(['python', 'GroupDParser.py'])

# List of CSV files to combine
csv_files = ['CombinedStatsGroupA.csv','CombinedStatsGroupAV2.csv', 'CombinedStatsGroupAV3.csv', 'CombinedStatsGroupB.csv', 'CombinedStatsGroupBV2.csv', 'CombinedStatsGroupD.csv']

# Initialize an empty DataFrame
combined_df = pd.DataFrame()

# Concatenate CSV files
for i, file in enumerate(csv_files):
    temp_df = pd.read_csv(file)

    # Rename columns with a unique suffix
    temp_df = rename_columns(temp_df, f'team_{i}')

    # Concatenate the DataFrames
    combined_df = pd.concat([pd.read_csv(file) for file in csv_files], axis=0, ignore_index=True)

# Save the combined data to a new CSV file
combined_df = combined_df.sort_values('Team')

combined_df.to_csv('NCAAD3StatsMaster.csv', index=False)

endTime = time.time()
totalTime = endTime - startTime

totalTime = totalTime / 60
print(f"Time: {totalTime} minutes")

#looking for 1747 individuals