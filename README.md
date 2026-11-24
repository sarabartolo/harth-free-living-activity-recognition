# Recognising Everyday Activities from Wearable Accelerometers

CT4101 Machine Learning portfolio project, MSc Health Data Science, University of Galway.

## Project question
Can a machine learning model trained on some participants' thigh and lower-back accelerometer data correctly classify the activities of unseen participants?

## Motivation
My background is in sport and exercise science, with a focus on biomechanics, and I'm interested in how wearable sensors can measure physical activity outside the lab. I chose this dataset because it was recorded in free-living conditions rather than through scripted lab tasks, so it reflects the messier data that real-world studies have to work with.

## Dataset
**HARTH (Human Activity Recognition Trondheim)**, UCI Machine Learning Repository.
- 22 adults wore two triaxial accelerometers (right front thigh and lower back) in free-living conditions, with activities labelled from video.
- About 35 hours of data across 12 activity labels.
- Licence: CC BY 4.0, which permits reuse with credit.

## Folder structure
```
├── data/
│   ├── raw/            # HARTH CSV files (not tracked by Git)
│   ├── processed/      # Windows table created by notebook 02 (not tracked by Git)
│   └── README.md       # Download instructions, licence and citation
├── notebooks/          # Numbered notebooks, run in order
│   ├── 01_data_inspection.ipynb  
│   ├── 02_preprocessing.ipynb
│   ├── 03_baseline.ipynb     
│   ├── 04_model_comparison.ipynb
│   ├── 05_pca.ipynb
│   └── 06_test_evaluation.ipynb
├── src/                 # Reusable Python functions
│   └── preprocessing.py # Cleaning, windowing and feature functions
├── reports/             # Proposal and report
│   └── figures/         # Figures used in the report
├── decision_log.md      # Project decisions and reasoning
├── ai_use_log.md        # Record of AI assistance
├── requirements.txt     # Package versions
└── README.md
```

## Setup
Created and tested on Windows 11 with Python 3.13.15.

1. Clone the repository:
```
   git clone https://github.com/sarabartolo/harth-free-living-activity-recognition.git
   cd harth-free-living-activity-recognition
```
2. Create and activate a virtual environment:
```
   py -m venv .venv
   .venv\Scripts\activate
```
   On macOS or Linux: `python3 -m venv .venv` then `source .venv/bin/activate`.

3. Install packages:
```
   pip install -r requirements.txt
```
   Note: `pywinpty` is Windows-only. On macOS or Linux, remove that line from requirements.txt before installing.

4. Download the data into `data/raw/` following data/README.md.

## How to run
1. Activate the environment (step 2 above) from the main project folder.
2. Start Jupyter: `jupyter lab`
3. Open the `notebooks` folder and run the notebooks in number order:
   - `01_data_inspection.ipynb`: data audit (does not change the data)
   - `02_preprocessing.ipynb`: cleans the data and creates `data/processed/harth_windows.csv`. This must be run before any later notebooks, because the processed file is not included in the repository.
   - `03_baseline.ipynb`: splits participants into training (18) and test (4) sets, sets up 5-fold grouped cross-validation, and evaluates a dummy baseline and logistic regression. Requires `data/processed/harth_windows.csv` from notebook 02.
   - `04_model_comparison.ipynb`: tunes and compares kNN, a decision tree, a random forest, gradient boosting and an MLP against the baselines, using the same grouped 5-fold cross-validation, and repeats the MLP with three extra seeds. Requires `data/processed/harth_windows.csv`.
   - `05_pca.ipynb`: exploratory PCA of the window features. Can be run on its own after notebook 02.
   - `06_test_evaluation.ipynb`: fits the final random forest and the MLP (for comparison) on all 18 training participants, and evaluates them once on the 4 test participants, with confusion matrices and per-participant scores. Requires `data/processed/harth_windows.csv`.

## Results
Results from 5-fold cross-validation on the 18 training participants (mean ± SD):

| Model | Macro F1 | Balanced accuracy | Training time (s) | Prediction time (s) |
|---|---|---|---|---|
| Dummy (most frequent class) | 0.081 ± 0.007 | 0.125 ± 0.000 | 0.06 | 0.11 |
| Logistic regression | 0.809 ± 0.039 | 0.802 ± 0.036 | 3.78 | 0.14 |
| kNN (k = 15, Manhattan) | 0.808 ± 0.030 | 0.799 ± 0.047 | 0.18 | 12.67 |
| Decision tree (depth 10, leaf 50) | 0.776 ± 0.037 | 0.775 ± 0.049 | 2.45 | 0.11 |
| Random forest (no depth limit, leaf 1) | 0.832 ± 0.009 | 0.835 ± 0.025 | 18.79 | 0.28 |
| Gradient boosting (0.02, 600 rounds, 15 leaves) | 0.814 ± 0.023 | 0.823 ± 0.022 | 26.92 | 1.60 |
| MLP (16 neurons, alpha 0.01) | 0.841 ± 0.022 | 0.833 ± 0.032 | 34.00 | 0.12 |

Times are per fold, in seconds, measured on a laptop, so they are useful for comparing models rather than as absolute values.

The MLP had the highest mean macro F1 (0.841, seed 42), but across four seeds it averaged 0.831 ± 0.008 (range 0.821 to 0.841), level with the random forest. **The random forest was chosen as the final model before testing**, because it was the most consistent across folds, and simpler and faster to train. The MLP had the best stairs F1 in cross-validation (0.567) and was evaluated on the test set as a comparison.

All models struggled with shuffling and stairs (F1 around 0.45 to 0.57), which are often confused with standing and walking. Exploratory PCA showed that these activities overlap with their neighbours in feature space.

## Final test results
Both models were trained on all 18 training participants and evaluated once on the 4 test participants (S018, S019, S022 and S025).

| Model | CV macro F1 | Test macro F1 | CV balanced accuracy | Test balanced accuracy |
|---|---|---|---|---|
| Random forest (final) | 0.832 ± 0.009 | 0.839 | 0.835 ± 0.025 | 0.836 |
| MLP (seed 42) | 0.841 ± 0.022 | 0.811 | 0.833 ± 0.032 | 0.818 |

The random forest's test score matched its cross-validation estimate, so it performed as expected on new participants. Per-participant macro F1 ranged from 0.76 to 0.91. Stairs scored higher on the test set than in cross-validation (F1 0.615 compared with 0.459) and shuffling lower (0.413 compared with 0.505), but both classes are small, so these differences probably reflect individuals. The MLP's lower test score came mainly from one participant (S025), who contributed most of the test cycling and whose cycling it often predicted as stairs.

## Limitations
- 22 healthy adults aged 25-68, so the model may not generalise to children, adults over 68, or people whose movement differs because of a health condition or impairment.
- Labels were annotated manually from video, so some may be wrong, especially at transitions between activities.
- Some activities come mostly from a few participants, which limits how well they can be learned and evaluated.
- Windows containing more than one activity were dropped (4.5%), so results reflect single-activity periods and may overestimate performance around transitions.
- Shuffling and stairs remain hard to classify for every model (F1 of 0.57 or below), likely because the features describe the amount and direction of movement but not its shape or rhythm.
- Tuned scores are slightly optimistic, because settings were chosen and scored on the same folds (no nested cross-validation).
- The test set has only 4 participants, so test results for some activities depend heavily on individuals.

## Intended use
Project for CT4101 Machine Learning Module.

## References
- A. Logacjov, K. Bach, A. Kongsvold, H. Bårdstu, and P. Mork, "HARTH: A Human Activity Recognition Dataset for Machine Learning," *Sensors*, vol. 21, no. 23, p. 7853, 2021, doi: 10.3390/s21237853.
- A. Logacjov, A. Kongsvold, K. Bach, H. Bårdstu, and P. Mork, "HARTH," UCI Machine Learning Repository, 2021, doi: 10.24432/C5NC90.
