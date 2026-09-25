## Log Decisions Made in Each Session
### 25-09-2026: 
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

