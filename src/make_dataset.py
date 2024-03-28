import os
import pandas as pd
import numpy as np
from utils import segmentation_events, event_length, GRID_SIZE, TIME_STEPS_PER_DAY
import argparse
import re

class DatasetCreator:
    """
    Class to create a dataset for a specific year and month.
    """
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.month_names = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    
    @staticmethod
    def get_date_from_file(file):
        match = re.search(r'(\d{4})(\d{2})(\d{2})', file)
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    
    @staticmethod
    def event_stats(raw_data, i, j, start_time, duration):
        events = raw_data[start_time:start_time+duration, i, j]
        events = events[~np.isnan(events)]
        return duration, np.max(events), np.mean(events), np.var(events), 1 - np.count_nonzero(events) / duration

    def extract_df_month(self):
        print(f"Listing all files for {self.year}-{self.month}.")
        files = os.listdir(f'data/raw_data/{self.year}')
        dates = [self.get_date_from_file(file) for file in files if file.endswith('.npy')]
        dates = [date for date in dates if date[1] == self.month]

        print(f"Total files for {self.month}/{self.year}: {len(dates)}")
        rows = []
        max_count = GRID_SIZE ** 2 * len(dates)
        count = 0
        for index, (year, month, day) in enumerate(dates):
            print(f"Processing file {index + 1}/{len(dates)}: {day}/{month}/{year}")
            raw_events, raw_data = segmentation_events(year, month, day)
            events = event_length(raw_events)
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if count % 1000 == 0:
                        print(f"{day}/{month}/{year}: {count} / {max_count}")
                    count += 1
                    for event_index, (start_time, duration) in enumerate(events[i, j]):
                        stats = self.event_stats(raw_data, i, j, start_time, duration)
                        rows.append({
                            'year': year, 'month': month, 'day': day, 
                            'i': i, 'j': j, 
                            'start_time_relative': start_time, 
                            'start_time_absolute': start_time + TIME_STEPS_PER_DAY * (day - 1), 
                            'duration': duration, 
                            'max_intensity': stats[1], 'mean_intensity': stats[2], 
                            'variance': stats[3], 'percentage_null': stats[4]
                        })
        print("Data extraction complete.")
        return pd.DataFrame(rows)


    def write_df_month(self):
        print(f"Extracting dataframe for {self.year}, {self.month_names[self.month-1]}")
        df = self.extract_df_month()
        df['end_time_absolute'] = df['start_time_absolute'] + df['duration']
        
        directory = 'data/dataframes'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        file_path = f'{directory}/{self.year}_{self.month}.pkl'
        df.to_pickle(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create dataset for a specific year and month, save to .pkl')
    parser.add_argument('-y', '--year', default=2020, type=int, required=False, help='The year of the dataset.')
    parser.add_argument('-s', '--start_month', default=6, type=int, required=False, help='The start month for which the dataset will be created.')
    parser.add_argument('-e', '--end_month', default=12, type=int, required=False, help='The end month for which the dataset will be created.')
    args = parser.parse_args()

    for month in range(args.start_month, args.end_month + 1):
        dc = DatasetCreator(args.year, month)
        dc.write_df_month()