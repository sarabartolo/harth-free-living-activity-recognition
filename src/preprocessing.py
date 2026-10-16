""" Pre processing """

# Imports
import numpy as np
import pandas as pd

# Set constants
SENSOR_COLS = ["back_x", "back_y", "back_z", "thigh_x", "thigh_y", "thigh_z"]

LABEL_DICT = { 1: "walking", 
              2: "running", 
              3: "shuffling", 
              4: "stairs", # changed from stairs (ascending)
              5: "stairs", # changed from stairs (descending)
              6: "standing", 
              7: "sitting", 
              8: "lying",
              13: "cycling", # changed from cycling (sit)
              14: "cycling"} # changed from cycling (stand)

# Left out 130: "cycling (sit, inactive)" & 140: "cycling (stand, inactive)"

WINDOW_SIZE = 50

GAP_MARGIN = 1.5

# Create Function to clean participant data
def clean_participant(file_path):
    """ This function reads in one participant's csv file, selects the timestamp, 
    sensor columns and labels to keep, adds a subject column containing participant ID, 
    maps the activity label number to the activity type from LABEL_DICT, drops the 
    inactive cycling rows, resamples from 100Hz to 50Hz if necessary,
    and returns the cleaned DataFrame """ 
    
    # Read one csv file from the HARTH dataset 
    df = pd.read_csv(file_path)
    
    # Select columns to keep
    data = df[["timestamp"] + SENSOR_COLS + ["label"]]

    # Convert Time from str to datetime64
    data["timestamp"] = pd.to_datetime(data["timestamp"])

    # Add subject column
    data["subject"] = file_path.stem

    # Map number to label using the label dictionary
    data["activity"] = data["label"].map(LABEL_DICT)

    # Drop inactive cycling rows
    data = data.dropna(subset=["activity"])

    # Find the time between each row and the median time for a participant
    time_between_rows = data["timestamp"].diff()
    step = time_between_rows.median()

    # Sampling rate for participants was 100Hz (step is 10ms) or 50 Hz (step is 20ms)
    # If time between steps is less than 15ms, sampling rate for the participant is 100Hz
    # Resample to 50 Hz by keeping every second row 
    if step < pd.Timedelta("15ms"):
        data = data.iloc[::2]

    # Renumber rows after Resampling
    data = data.reset_index(drop=True)

    return data



    
# Create Function to Create Windows

def create_windows(data):
    """ This function takes a cleaned DataFrame, creates a new block at every time gap, 
    creates a window every 50 rows in each block, only keeps windows with 50 rows, and 
    one activity, and returns the rows from full, single-activity windows, with block, 
    window and window_n columns """   
    
    data = data.copy()
    
    # Find the time between each row and the median time for a participant
    time_between_rows = data["timestamp"].diff()
    step = time_between_rows.median()

    # Create a new block each time the time between rows is 1.5 times the median step time
    new_block = time_between_rows > step * GAP_MARGIN # True = gap
    data["block"] = new_block.cumsum()

    # Counts the rows in each block and create a window every 50 rows
    # Once the block ends move onto the next and start from 0
    data["window"] = data.groupby("block").cumcount() // WINDOW_SIZE

    # Count the rows in each window 
    window_size = data.groupby(["block", "window"])["label"].transform("size")

    # Only keep windows with 50 rows
    data = data[window_size == WINDOW_SIZE]

    # Give each window a unique number to make them independepent of blocks
    data["window_n"] = data.groupby(["block", "window"]).ngroup()

    # Drop all windows that contain more than one activity
    activities_per_window = data.groupby("window_n")["activity"].nunique()
    one_activity_per_window = activities_per_window[activities_per_window == 1].index
    data = data[data["window_n"].isin(one_activity_per_window)]

    return data

    
def create_features(data): 
    """This function adds a vector magnitude column for each sensor, the mean, 
    sd and ranges of the six sensor columns and two vector magnitude columns, 
    adds the subject and activity columns, and then returns a DataFrame containing 
    one row per window, with 24 features, activity and subject """
     
    data = data.copy()
    
    # Add vector magnitude columns
    data["back_mag"] = np.sqrt(data["back_x"]**2 + data["back_y"]**2 + data["back_z"]**2)
    data["thigh_mag"] = np.sqrt(data["thigh_x"]**2 + data["thigh_y"]**2 + data["thigh_z"]**2)
    
    # Group together the feature columns and windows to get the mean, sd & range
    feature_cols = SENSOR_COLS + ["back_mag", "thigh_mag"] 
    group = data.groupby("window_n")[feature_cols]
    
    means = group.mean().add_suffix("_mean")
    sds = group.std().add_suffix("_sd")
    ranges = (group.max() - group.min()).add_suffix("_range")
    
    windows = pd.concat([means,sds,ranges], axis=1)
    
    # Add the activity type and subject to the df
    windows["activity"] = data.groupby("window_n")["activity"].first() # Take the first activity of each window 
    windows["subject"] = data.groupby("window_n")["subject"].first()
    
    return windows