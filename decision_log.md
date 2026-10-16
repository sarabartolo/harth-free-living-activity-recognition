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

## 16-10-2026: Finished data preprocessing on all participants
#### Notes
- In the clean_participant() function, I resampled participant from 100Hz to 50 Hz by keeping every second row since this is the simplest method of downsampling. 
- Final dataset has 118,386 windows from 22 participants.
- Dropping mixed windows removed more of the short, transitional activities like shuffling, stairs compared to the others.

## 16-10-2026: Baseline Models
- Train/test split by participant: 18 training, 4 test (S018, S019, S022, S025), so the model is tested on people it hasn't seen. The test set is 22,308 windows (19%).
- Test participants were chosen manually from a crosstab of windows per activity, before any modelling, so that:
  - all 8 activities appear in both the training and test sets
  - the main contributors to running (S027) and cycling (S009, S026) stay in training
  - both recording groups are represented in the test set (S025 is from the S023 to S029 group)
- A random split wasn't used because several activities come mainly from one or two participants, so a random choice of four could leave an activity missing or barely represented in one set.
- Limitation: much of the test set's cycling comes from S025, so the test result for cycling mostly reflects one person.
- After the split, the test participants are set aside and are not used for any decision. The test set will be used once, at the end, after the final model is chosen.
- Cross-validation: 5-fold StratifiedGroupKFold on the 18 training participants. Grouping keeps each participant in one fold; stratification keeps the activity mix similar across folds, so no validation fold is missing a rare activity. 5 gives 3 to 4 participants per fold.

#### Decisions: baselines and metrics
- Two baselines: a dummy model that always predicts the most common class (sitting), and logistic regression as a simple learned baseline.
- Logistic regression is in a pipeline with StandardScaler, so the scaler is fitted on the training participants of each fold only.
- Main metric: macro F1 (every activity weighted equally despite the imbalance). Secondary metric: balanced accuracy (macro-averaged recall), which is easier to interpret than F1 and not inflated by the large sitting class like plain accuracy would be.

#### Results (5-fold cross-validation, mean ± SD)
| Model | Macro F1 | Balanced accuracy |
|---|---|---|
| Dummy (most frequent) | 0.081 ± 0.007 | 0.125 ± 0.000 |
| Logistic regression | 0.809 ± 0.039 | 0.802 ± 0.036 |

- Logistic regression recognises sitting, lying, running, standing, walking and cycling well (0.89 to 1.00 recall).
- Weak classes: shuffling (0.38), mostly confused with standing and walking, and stairs (0.35), mostly confused with walking. These movements look similar to walking or standing in 1-second summary features, and they also lost the most windows when mixed windows were dropped.