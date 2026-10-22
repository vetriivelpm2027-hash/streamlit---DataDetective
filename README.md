# 🔎 Data Detective — Intelligent CSV Investigation Platform

Data Detective is an interactive CSV investigation application built with **Python**, **Pandas**, **NumPy**, **Matplotlib**, and **Streamlit**. It helps users explore datasets, inspect data quality, visualize patterns, review potential anomalies, clean data, and compare two versions of a CSV file.

## ✨ Features

- **Dashboard** — view a quick overview of the uploaded dataset.
- **Data Explorer** — inspect dataset rows, columns, and structure.
- **Quality Inspector** — review missing values and duplicate records.
- **Anomaly Detection** — identify potentially unusual numerical values for further review.
- **Visual Analytics** — explore data patterns using charts.
- **Clean & Export** — clean data and export the resulting dataset, based on the implemented options.
- **Dataset Comparison** — compare old and new CSV files to find new, deleted, and modified records.
- **Downloadable report** — export Dataset Comparison results as a JSON file.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | CSV loading, data manipulation, and analysis |
| NumPy | Numerical calculations |
| Matplotlib | Data visualization |
| Streamlit | Interactive web interface |
| JSON | Comparison report export |

## 📋 Requirements

- Python 3.10 or a compatible Python version
- `streamlit`
- `pandas`
- `numpy`
- `matplotlib`

## 🚀 Installation and Setup

### 1. Download or clone the project

If the project is hosted on GitHub, clone it:

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

Alternatively, download the project ZIP and extract it.

### 2. Install dependencies

Open a terminal in the project folder and run:

```bash
python -m pip install streamlit pandas numpy matplotlib
```

### 3. Run the application

```bash
python -m streamlit run app.py
```

Streamlit will show a local URL in the terminal. Open that URL in your browser.

## 📂 Project Structure

```text
Data-Detective/
├── app.py
├── README.md
└── (optional project CSV files and documentation)
```

> Your folder may contain additional files depending on your final project version.

## 📊 Using Dataset Comparison

1. Open **Dataset Comparison** from the app's sidebar.
2. Upload the old CSV file in the first CSV uploader.
3. Upload the new CSV file in the second CSV uploader.
4. Select a shared, unique ID column from the dropdown.
5. Review the new, deleted, and modified record counts.
6. Open the result sections to inspect the records.
7. Download the comparison report in JSON format if needed.

### Example data

**Old dataset (`sample_old.csv`)**

```csv
ID,Name,Score
1,Arun,80
2,Priya,90
3,Kumar,70
```

**New dataset (`sample_new.csv`)**

```csv
ID,Name,Score
1,Arun,85
2,Priya,90
4,Divya,95
```

Expected comparison:

| Result | Expected |
|---|---|
| New records | 1 — Divya (ID 4) |
| Deleted records | 1 — Kumar (ID 3) |
| Modified records | 1 — Arun's score changed from 80 to 85 |

### Important notes

- Upload valid, non-empty CSV files with column headers.
- Both files must contain at least one column with the same name.
- Choose an ID column that has no missing values and no duplicates in either file.
- The app compares values in shared columns. A value flagged as an anomaly is only a potential issue and should be checked in context.

## 🎯 Project Objectives

- Make CSV data easier to inspect and understand.
- Help identify common data-quality issues.
- Visualize numerical data and patterns.
- Compare dataset versions efficiently.
- Demonstrate practical use of NumPy and Pandas in a Python application.

## 🔮 Future Improvements

- Add Excel file support.
- Generate PDF summary reports.
- Add configurable anomaly-detection methods.
- Add user login and saved analysis history.
- Improve performance for very large datasets.

## 👩‍💻 Author

**Name:** *Add your name here*  
**Project:** Data Detective — Intelligent CSV Investigation Platform  
**Technology:** Python, NumPy, Pandas, Matplotlib, Streamlit

---

⭐ If you find this project useful, feel free to star the repository.
