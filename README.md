# Recognising Everyday Activities from Wearable Accelerometers

CT4101 Machine Learning portfolio project, MSc Health Data Science, University of Galway.

### Project question
Can a machine learning model trained on some participants' thigh and lower-back accelerometer data correctly classify the activities of unseen participants?

### Motivation
My background is in sport and exercise science, with a focus on biomechanics, and I'm interested in how wearable sensors can measure physical activity outside the lab. I chose this datset because it was recorded in free-living conditions rather than through scripted lab tasks, so it reflects the messier data that real-world studies have to work with.

### Dataset
**HARTH (Human Activity Recognition Trondheim)**, UCI Machine Learning Repository.
- 22 adults wore two triaxial accelerometers (right front thigh and lower back) in free-living conditions, with activities labelled from video.
- About 35 hours of data across 12 activity labels.
- Licence: CC BY 4.0, which permits reuse with credit.

Decisions and the reasons for them are recorded in decision_log.md

### Folder structure
```
├── data/
│   ├── raw/            # HARTH CSV files (not tracked by Git)
│   └── README.md       # Download instructions, licence and citation
├── notebooks/          # Numbered notebooks, run in order
├── src/                # Reusable Python functions
├── reports/            # Proposal and report
├── decision_log.md     # Project decisions and reasoning
├── ai_use_log.md       # Record of AI assistance
├── requirements.txt    # Package versions
└── README.md
```

### Setup
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

### How to run
1. Activate the environment (step 2 above) from the main project folder.
2. Start Jupyter: `jupyter lab`
3. Open the `notebooks` folder and run the notebooks in number order:
   - `01_data_inspection.ipynb`: data audit
   - 

### Results
To be added.

### Limitations
- 22 healthy adults aged 25-68, so the model may not generalise to children, adults over 68, or people whose movement differs because of a health condition or impairment.
- Labels were annotated manually from video, so some may be wrong, especially at transitions between activities.
- Some activities come mostly from a few participants, which limits how well they can be learned and evaluated.

### Intended use
Project for CT4101 Machine Learning Module.

### References
- A. Logacjov, K. Bach, A. Kongsvold, H. Bårdstu, and P. Mork, "HARTH: A Human Activity Recognition Dataset for Machine Learning," *Sensors*, vol. 21, no. 23, p. 7853, 2021, doi: 10.3390/s21237853.
- A. Logacjov, A. Kongsvold, K. Bach, H. Bårdstu, and P. Mork, "HARTH," UCI Machine Learning Repository, 2021, doi: 10.24432/C5NC90.
