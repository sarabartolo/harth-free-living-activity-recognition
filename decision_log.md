## Log Decisions Made in Each Session
## 25-09-2026: 
#### Notes
- Chose the HARTH dataset from UCI (https://archive.ics.uci.edu/dataset/779/harth). It contains free-living data from wearable sensors (attached to right front thigh and lower back)
- After the initial data inspection, I found that sampling differs between subjects so row counts weren't comparable. I inspected activity counts in minutes instead
- Will split train/test data by subject so that the model is tested on subjects it has not seen yet. This is also more representative of future data

#### Findings from Inspection
- 22 participants, 12 activity labels, no missing values and no duplicate timestamps
- Mixed sampling rates: S006 is 100Hz and others are 50Hz
- 3 subjects has extra columns: S015 and S021 have an extra 'index' column as their second column and S023 has extra 'Unnamed: 0' column as the first column
- There are a small number of timestamo gaps in all subjects 
- Sitting makes up a large amount of the data, followed by walking and standing...
- Some activities come mostly from a few subjects e.g. running mainly comes from S027, and cycling mainly comes from "S026 and S009
- Some activities also have very little data: stairs (ascending): 25.20mins, stairs (descending): 22.16mins, cycling (stand): 18.09mins, cycling (sit, inactive): 12.04mins, cycling (stand, inactive): 2.62.

#### Need to Decide:
- Which activities should I include? drop cycling? merge stairs ascending and descending?
- Which subjects should go in test set and which in the training set? need to make sure that each activity i include is well represented in both sets
-Need to handle sampling rate issue - probably just resample S006 to 50Hz to match the other subjects

## 02-10-2026

#### Decisions (made while writing the proposal)
- Classes: reduced from 12 to 8 (sitting, walking, standing, lying, running, shuffling, stairs, cycling).
  - Merged stairs ascending and descending into 'stairs' because each has too little data on its own.
  - Merged cycling (sit) and cycling (stand) into 'cycling' for the same reason.
  - Dropped both inactive cycling labels. They have about 15 min of data combined, and sitting or standing still on a bike probably looks like sitting or standing to the sensors, so merging them into 'cycling' would add label noise.
- Data cleaning: resample S006 to 50 Hz to match the other subjects. Drop the extra 'index' and 'Unnamed: 0' columns.
- Windows: non-overlapping 1-second windows (50 samples at 50 Hz), following Logacjov et al. (2021). This gives about 126,000 windows.
- Features: mean, standard deviation and range of each axis and of each sensor's vector magnitude, √(x²+y²+z²). Vector magnitude captures overall movement intensity regardless of sensor orientation.
- Baseline: always predict the most common class (sitting).
- Candidate models: decision tree (interpretable), k-NN (similarity to training windows), SVM (suited to many features).
- Evaluation design: hold out a few subjects as a test set, chosen so every class is present, and use it only once at the end. Tune with cross-validation grouped by subject on the rest.
- Metrics: F1 score as the main metric because it weights every activity equally despite the imbalance. Confusion matrix to show which activities get confused.
- Leakage prevention: split by subject; fit scaling on training data only; don't use timestamp or index columns as features.

#### Need to decide
- Which subjects go in the test set, making sure each class is represented in both training and test sets.
- How to handle windows that span a timestamp gap or contain two activities (drop them, or label them by the majority activity?).
- Whether to add a gravity/movement feature (thigh tilt) from the paper's approach

## 10-10-2026 - Completed data inspection
#### Findings & Decisions
- Sensors were set to ± 8g (Logacjov et al., 2021, page 6)
- 188 cells hit the limit, all during walking and running, mostly in S027 and S029. Since the limit was hit during high-impact activities and in very few instances I kept all the data. Note: S029 reached the sensor limits most during walking which is unusual
- Most gaps in the time series were more than 1 seconds so I need to account for them when creating the windows

## 2026-10-10 - Started data preprocessing (on one participant)
#### Notes
- Kept the timestamp, sensor, and label columns, dropped index/unnamed column, and added subject column
- Addeded activity column, mapping labels to their activity. I merged 'stairs (ascending/descending)' into 'stairs' and 'cycling (sit/stand)' into 'cylcing'. I also dropped inactive cycling labels
- Created blocks, where a new block started after a gap (a gap is any time between two rows longer than the median time of the participant)
- Created 1-second non-overlapping windows (50 rows) 
- Dropped window < 1s and containing more than 1 activity
- Computed vector magnitude of the 2 sensors
- Computed features for each window: mean, standard deviation & range for the six axes and 2 vector magnitudes

#### To do next
- Resample S006 from 100 Hz to 50Hz
- Repeat preprocessing for the rest of the participants and create one dataframe
- Decide training/text split
- Sitting dummy baseline & simple learned baseline

### 16-10-2026: Continued data preprocessing on all participants
#### Notes
- In the clean_participant() function, I resampled participant from 100Hz to 50 Hz by keeping every second row since this is the simplest method of downsampling. 