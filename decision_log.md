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
- Candidate models: decision tree (interpretable), kNN (similarity to training windows), SVM (suited to many features).
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

## 08-11-2026: Models

#### Decisions: model choice
- Models: kNN and decision tree, then random forest and gradient boosting, compared against the dummy and logistic regression baselines. Ordered from simple to complex.
- All models use the same training participants, the same 5 grouped folds and the same metrics. Tuning uses GridSearchCV with macro F1 to pick the best setting. The tuned model is then scored with cross_validate on the same folds.
- Limitation: the best setting is chosen and scored on the same folds, so its score is slightly optimistic. Nested cross-validation could have avoided this but has higher computation need and would have taken too long to run on my machine.
- Training and prediction time are recorded for each model.

#### kNN
- Grid: k 5, 15, 25, 45, 65; weights uniform/distance; p 1/2 (Manhattan/Manhattan). 
- Best: k = 15, uniform, Manhattan (p = 1). Macro F1 0.808 ± 0.030.
- Manhattan better than Euclidean at every k and more stable.
- Weighting made almost no difference bu uniform weighting was kept.
- Some more details in notebook

#### Decision tree
- Grid: max_depth 5, 10, 15, 20, 30, None; min_samples_leaf 1, 10, 50, 100, 200; criterion gini/entropy. random_state = 42.
- Best: gini, depth 10, leaf 50. Macro F1 0.776 ± 0.037.
- Overfitting with no limits (training 1.000, validation 0.737); depth 5 underfits.
- Top splits use thigh orientation, back orientation and thigh movement variability, which supports the choice of mean and SD features.
- Some more details in notebook

#### Results so far (5-fold CV, mean ± SD)
| Model | Macro F1 | Balanced accuracy | Training time (s) | Prediction time (s) |
|---|---|---|---|---|
| Dummy | 0.081 ± 0.007 | 0.125 ± 0.000 | 0.05 | 0.09 |
| Logistic regression | 0.809 ± 0.039 | 0.802 ± 0.036 | 3.82 | 0.14 |
| kNN | 0.808 ± 0.030 | 0.799 ± 0.047 | 0.18 | 12.56 |
| Decision tree | 0.776 ± 0.037 | 0.775 ± 0.049 | 2.59 | 0.14 |

#### To do
- Random forest: out-of-bag score will not be used, because the windows a tree doesn't sample still come from the same participants, so it would be optimistic.
- Gradient boosting
- Consider PCA (refer to week 8 notes)

## 10/11-11-2026: Models cont.

#### Random forest
- 200 trees. Grid: max_depth 10, 20, None × min_samples_leaf 1, 10, 50, kept small because each fit trains 200 trees - high compuation
- Best: no depth limit, leaf 1. Macro F1 0.832 ± 0.009. The forest is best with larger trees, because averaging cancels out each tree's overfitting (unlike decision tree single tree).
- Out-of-bag score not used

#### Gradient boosting
- HistGradientBoostingClassifier, early_stopping=False (default early stopping uses a random, ungrouped 10% of windows).
- First search best: learning_rate 0.05, 15 leaves (0.812). High learning rates were unstable.
- The best setting was at the edge of the grid, so a second search tried 0.02, 600 rounds and 5 leaves. Best: 0.02, 600 rounds, 15 leaves (0.814 ± 0.023). Very little gain, so stopped there.
- Kept both searches; used the second search's best model

#### Final cross-validation results (mean ± SD)
| Model | Macro F1 | Balanced accuracy | Training time (s) | Prediction time (s) |
|---|---|---|---|---|
| Dummy | 0.081 ± 0.007 | 0.125 ± 0.000 | 0.07 | 0.10 |
| Logistic regression | 0.809 ± 0.039 | 0.802 ± 0.036 | 4.18 | 0.14 |
| kNN | 0.808 ± 0.030 | 0.799 ± 0.047 | 0.18 | 12.12 |
| Decision tree | 0.776 ± 0.037 | 0.775 ± 0.049 | 2.90 | 0.16 |
| Random forest | 0.832 ± 0.009 | 0.835 ± 0.025 | 19.04 | 0.26 |
| Gradient boosting | 0.814 ± 0.023 | 0.823 ± 0.022 | 26.99 | 1.57 |

#### Conclusions so far
- Best model: random forest (highest and most consistent macro F1; better than logistic regression in 4 of 5 folds).
- Shuffling and stairs F1 stay around 0.45 to 0.5 for every model, so the limit is likely the features, not the models.
- Nested CV not used because of computation time; will note as a limitation.

#### To do next
- PCA, feature importance and the final test.
