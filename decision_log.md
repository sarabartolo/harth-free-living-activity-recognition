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

## 2026-10-02

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
