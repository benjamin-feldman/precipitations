from joblib import Parallel, delayed
import numpy as np

GRID_SIZE = 300
TIME_STEPS_PER_DAY = 288

def read_data(year, month, day):
    path = f'data/raw_data/{year:04d}/'
    file_name = f'RR_IDF300x300_{year:04d}{month:02d}{day:02d}.npy'
    full_path = path + file_name
    try:
        raw_data = np.load(full_path) / 100.0
        raw_data[raw_data < 0] = np.nan
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {full_path} does not exist.")
    return raw_data


def segmentation_events(year, month, day):
    raw_data = read_data(year, month, day)
    raw_events = np.zeros((TIME_STEPS_PER_DAY, GRID_SIZE, GRID_SIZE))

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            t = 0
            while t < TIME_STEPS_PER_DAY:
                if not np.isnan(raw_data[t, i, j]):
                    start = t
                    while t < TIME_STEPS_PER_DAY and not np.isnan(raw_data[t, i, j]):
                        raw_events[t, i, j] = 1
                        t += 1
                    # Applying a 30-minute rule for precipitation events
                    if t - start > 5:
                        raw_events[start:t, i, j] = 1
                t += 1
    return raw_events, raw_data

def event_length(raw_events):
    """
    Calculates the length of weather events.
    """
    lengths = np.empty((GRID_SIZE, GRID_SIZE), dtype=object)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            events = []
            t = 0
            while t < TIME_STEPS_PER_DAY:
                if raw_events[t, i, j] == 1:
                    start = t
                    while t < TIME_STEPS_PER_DAY and raw_events[t, i, j] == 1:
                        t += 1
                    events.append((start, t - start))
                else:
                    t += 1
            lengths[i, j] = events
    return lengths

def extract_time_series(year, month, day, pixels_indices: list):
    raw_data = read_data(year, month, day)
    res = []
    for i, j in pixels_indices:
        res.append(raw_data[:, i, j])