import numpy as np

GRID_SIZE = 300
TIME_STEPS_PER_DAY = 288

def segmentation_events(year, month, day):
    path = f'data/{year:04d}/'
    file_name = f'RR_IDF300x300_{year:04d}{month:02d}{day:02d}.npy'
    full_path = path + file_name
    raw_data = np.load(full_path) / 100.0
    raw_data[raw_data < 0] = np.nan

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
                    if t - start > 5:  # Applying a 30-minute rule for precipitation events
                        raw_events[start:t, i, j] = 1
                t += 1
    return raw_events, raw_data

def event_length(year, month, day):
    raw_events, raw_data = segmentation_events(year, month, day)
    # Initialize an empty array of objects
    lengths = np.empty((GRID_SIZE, GRID_SIZE), dtype=object)

    # Populate the array with empty lists
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            lengths[i, j] = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            events = []
            t = 0
            while t < TIME_STEPS_PER_DAY:
                if raw_events[t, i, j] == 1:
                    start = t
                    while t < TIME_STEPS_PER_DAY and raw_events[t, i, j] == 1:
                        t += 1
                    length = t - start
                    events.append((start, length))
                t += 1
            lengths[i, j] = events
    return lengths, raw_data

