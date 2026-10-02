# Data

The raw data is not included in this repository. Follow the steps below to download it.

## Source
**HARTH (Human Activity Recognition Trondheim)**
UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/779/harth
DOI: https://doi.org/10.24432/C5NC90
Downloaded: 17-09-2026

## Licence
Creative Commons Attribution 4.0 International (CC BY 4.0). The data may be shared and adapted for any purpose, as long as appropriate credit is given.

## Citation
A. Logacjov, K. Bach, A. Kongsvold, H. Bårdstu, and P. Mork, "HARTH: A Human Activity Recognition Dataset for Machine Learning," *Sensors*, vol. 21, no. 23, p. 7853, 2021, doi: 10.3390/s21237853.

## How to download
1. Go to the UCI page above and click **Download**.
2. Unzip the file.
3. Move the 22 CSV files directly into `data/raw/`.

The folder should then look like this:
```
data/
├── raw/
│   ├── S006.csv
│   ├── S008.csv
│   ├── ...
│   └── S029.csv
└── README.md
```

Expected files (22): S006, S008, S009, S010, S012, S013, S014, S015, S016, S017, S018, S019, S020, S021, S022, S023, S024, S025, S026, S027, S028, S029.

## Contents
One CSV file per participant, with one row per sensor reading.

| Column | Meaning |
|---|---|
| timestamp | Date and time of the reading |
| back_x, back_y, back_z | Acceleration from the lower-back sensor, three axes (in unit g) |
| thigh_x, thigh_y, thigh_z | Acceleration from the right front thigh sensor, three axes (in unit g) |
| label | Activity code (see below) |

Activity codes: 1 walking, 2 running, 3 shuffling, 4 stairs (ascending), 5 stairs (descending), 6 standing, 7 sitting, 8 lying, 13 cycling (sit), 14 cycling (stand), 130 cycling (sit, inactive), 140 cycling (stand, inactive).

## Known issues
- S006 is sampled at 100 Hz; all other files are at 50 Hz.
- S015 and S021 have an extra `index` column, and S023 has an extra `Unnamed: 0` column.
- Small timestamp gaps occur in all files.

These are handled in the notebooks.