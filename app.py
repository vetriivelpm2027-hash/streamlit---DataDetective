# Run command : python -m streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from io import BytesIO
from io import StringIO
from datetime import datetime

st.set_page_config(
    page_title="Data Detective | Analytics",
    page_icon="🔎",
    layout="wide"
)

# ---------------- CUSTOM UI ----------------

st.markdown("""
<style>
.stApp {
    background: #0b1120;
    color: #e2e8f0;
}
[data-testid="stSidebar"] {
    background: #111c30;
}
[data-testid="stMetric"] {
    background: #172337;
    border: 1px solid #293b55;
    padding: 16px;
    border-radius: 12px;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8;
}
h1, h2, h3 {
    color: #60a5fa;
}
.stButton button, .stDownloadButton button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.title("🔎 DATA DETECTIVE")
st.caption("INTELLIGENT CSV INVESTIGATION PLATFORM")

st.write(
    "Investigate datasets, discover anomalies, "
    "improve data quality and generate reports."
)

# ---------------- SIDEBAR ----------------

st.sidebar.title("🔎 Data Detective")
st.sidebar.caption("Analytics Workspace")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Data Explorer",
        "Quality Inspector",
        "Anomaly Detection",
        "Visual Analytics",
        "Clean & Export",
        "Dataset Comparison"
    ]
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV Dataset",
    type=["csv"]
)
comparison_file = st.sidebar.file_uploader(
    "Upload second CSV for comparison",
    type=["csv"],
    key="comparison_csv"
)

if uploaded_file is None:
    st.info("Upload a CSV file from the sidebar to start.")
    st.subheader("Your investigation toolkit")

    c1, c2, c3 = st.columns(3)
    c1.markdown("### 📊 Analytics\nExplore statistics and patterns.")
    c2.markdown("### 🛡️ Quality\nInspect missing and duplicate records.")
    c3.markdown("### 🧹 Cleaning\nPrepare and export clean datasets.")

    st.stop()

# ---------------- LOAD DATA ----------------

try:
    df = pd.read_csv(uploaded_file)
except Exception as error:
    st.error(f"Could not read the CSV file: {error}")
    st.stop()

if df.empty or len(df.columns) == 0:
    st.error("The uploaded CSV contains no usable data.")
    st.stop()

rows, cols = df.shape
missing = int(df.isna().sum().sum())
duplicates = int(df.duplicated().sum())
total_cells = rows * cols

missing_pct = missing / total_cells * 100 if total_cells else 0
duplicate_pct = duplicates / rows * 100 if rows else 0

quality_score = round(
    max(0, 100 - missing_pct * 0.7 - duplicate_pct * 0.3),
    2
)

numeric_df = df.select_dtypes(include=np.number)
categorical_df = df.select_dtypes(
    include=["object", "category", "bool"]
)

# ---------------- OUTLIER ANALYSIS ----------------

outlier_counts = {}

for col in numeric_df.columns:
    values = numeric_df[col].dropna()

    if values.empty:
        outlier_counts[str(col)] = 0
        continue

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        outlier_counts[str(col)] = 0
    else:
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_counts[str(col)] = int(
            ((values < lower) | (values > upper)).sum()
        )

# ---------------- DASHBOARD ----------------

if page == "Dashboard":
    st.header("📊 Investigation Dashboard")

    a, b, c, d = st.columns(4)
    a.metric("Total Rows", f"{rows:,}")
    b.metric("Total Columns", f"{cols:,}")
    c.metric("Missing Cells", f"{missing:,}")
    d.metric("Duplicate Rows", f"{duplicates:,}")

    st.subheader("Data Quality Score")

    st.progress(quality_score / 100)
    st.metric("Quality Score", f"{quality_score}/100")

    st.caption(
        "This score penalizes missing cells and duplicate rows. "
        "It does not measure every aspect of data accuracy."
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Column Types")
        type_counts = pd.Series({
            "Numerical": len(numeric_df.columns),
            "Categorical": len(categorical_df.columns),
            "Other": cols - len(numeric_df.columns)
            - len(categorical_df.columns)
        })
        st.bar_chart(type_counts)

    with right:
        st.subheader("Missing Values by Column")
        missing_by_col = df.isna().sum()
        missing_by_col = missing_by_col[missing_by_col > 0]

        if missing_by_col.empty:
            st.success("No missing values detected.")
        else:
            st.bar_chart(missing_by_col)

    st.subheader("Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

# ---------------- QUALITY INVESTIGATION ----------------


elif page == "Dataset Comparison":
    st.header("🔄 Dataset Comparison")
    st.write("Compare old and new CSV datasets.")

    if uploaded_file is None:
        st.warning("Please upload the first CSV file in the sidebar.")
        st.stop()

    if comparison_file is None:
        st.info("Upload the second CSV from the sidebar to begin comparison.")
        st.stop()

    try:
        if uploaded_file.size == 0 or comparison_file.size == 0:
            st.error("CSV file is empty. Please upload valid CSV files.")
            st.stop()

        old_df = pd.read_csv(BytesIO(uploaded_file.getvalue()))
        new_df = pd.read_csv(BytesIO(comparison_file.getvalue()))

    except pd.errors.EmptyDataError:
        st.error("CSV file has no column headers or data.")
        st.stop()

    except Exception as error:
        st.error(f"Unable to read CSV: {error}")
        st.stop()

    common_cols = [
        col for col in old_df.columns
        if col in new_df.columns
    ]

    if not common_cols:
        st.error("No common columns found in both CSV files.")
        st.stop()

    st.subheader("📊 Dataset Overview")

    c1, c2 = st.columns(2)
    c1.metric("Old Dataset Rows", len(old_df))
    c2.metric("New Dataset Rows", len(new_df))

    st.write("Common columns:", ", ".join(map(str, common_cols)))

    key_col = st.selectbox(
        "Select a unique ID column",
        common_cols
    )

    if old_df[key_col].isna().any() or new_df[key_col].isna().any():
        st.error("The ID column contains missing values.")
        st.stop()

    if old_df[key_col].duplicated().any() or new_df[key_col].duplicated().any():
        st.error("The ID column must contain unique values in both datasets.")
        st.stop()

    old = old_df.set_index(key_col)
    new = new_df.set_index(key_col)

    old_ids = set(old.index)
    new_ids = set(new.index)

    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids
    shared_ids = old_ids & new_ids

    compare_cols = [
        col for col in common_cols if col != key_col
    ]

    changed_records = []

    for record_id in shared_ids:
        changed_fields = {}

        for col in compare_cols:
            old_value = old.at[record_id, col]
            new_value = new.at[record_id, col]

            both_missing = pd.isna(old_value) and pd.isna(new_value)

            if both_missing:
                continue

            if not both_missing and old_value == new_value:
                continue

            changed_fields[col] = {
                "old": old_value,
                "new": new_value
            }

        if changed_fields:
            changed_records.append({
                "ID": str(record_id),
                "Changes": changed_fields
            })

    st.subheader("🔍 Comparison Results")

    a, b, c = st.columns(3)
    a.metric("🆕 New Records", len(added_ids))
    b.metric("🗑️ Deleted Records", len(removed_ids))
    c.metric("✏️ Modified Records", len(changed_records))

    with st.expander("View New Records"):
        st.dataframe(
            new_df[new_df[key_col].isin(added_ids)],
            use_container_width=True
        )

    with st.expander("View Deleted Records"):
        st.dataframe(
            old_df[old_df[key_col].isin(removed_ids)],
            use_container_width=True
        )

    with st.expander("View Modified Records"):
        if changed_records:
            st.json(changed_records)
        else:
            st.success("No modified records found.")

    report = {
        "id_column": str(key_col),
        "new_records": len(added_ids),
        "deleted_records": len(removed_ids),
        "modified_records": len(changed_records),
        "added_ids": [str(x) for x in added_ids],
        "removed_ids": [str(x) for x in removed_ids],
        "changes": changed_records
    }

    st.download_button(
        "⬇️ Download Comparison Report",
        data=json.dumps(report, indent=4, default=str),
        file_name="comparison_report.json",
        mime="application/json"
    )


# ---------------- DATA EXPLORER ----------------

elif page == "Data Explorer":
    st.header("🗂️ Data Explorer")

    search = st.text_input("Search column names")

    visible_cols = [
        col for col in df.columns
        if search.lower() in str(col).lower()
    ]

    if visible_cols:
        st.dataframe(
            df[visible_cols],
            use_container_width=True
        )
    else:
        st.warning("No columns match your search.")

    st.subheader("Column Information")

    info = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Type": df.dtypes.astype(str).values,
        "Missing": df.isna().sum().values,
        "Unique": df.nunique().values
    })

    st.dataframe(info, use_container_width=True)

    with st.expander("Statistical Summary"):
        st.dataframe(
            df.describe(include="all").transpose(),
            use_container_width=True
        )

# ---------------- QUALITY INSPECTOR ----------------

elif page == "Quality Inspector":
    st.header("🛡️ Quality Inspector")

    missing_report = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Missing Count": df.isna().sum().values,
        "Missing %": (
            df.isna().mean().values * 100
        ).round(2)
    })

    st.subheader("Missing Values")
    st.dataframe(missing_report, use_container_width=True)

    st.subheader("Duplicate Records")
    st.write(f"Detected duplicate rows: **{duplicates}**")

    if missing == 0 and duplicates == 0:
        st.success("No missing cells or duplicate rows detected.")
    else:
        st.warning("Review the detected data quality issues.")

    st.subheader("Constant Columns")

    constant_cols = [
        col for col in df.columns
        if df[col].nunique(dropna=False) <= 1
    ]

    if constant_cols:
        st.write(constant_cols)
    else:
        st.success("No constant columns detected.")

# ---------------- ANOMALY DETECTION ----------------

elif page == "Anomaly Detection":
    st.header("🚨 Anomaly Detection")
    st.caption("Numerical outliers detected using the IQR method.")

    if numeric_df.empty:
        st.info("No numerical columns found.")
    else:
        report = pd.DataFrame({
            "Column": list(outlier_counts.keys()),
            "Outlier Count": list(outlier_counts.values())
        })

        st.dataframe(report, use_container_width=True)

        selected = st.selectbox(
            "Inspect a numerical column",
            list(numeric_df.columns)
        )

        values = numeric_df[selected].dropna()

        if not values.empty:
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1

            if iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr

                unusual = values[
                    (values < lower) | (values > upper)
                ]

                st.write("Lower threshold:", float(lower))
                st.write("Upper threshold:", float(upper))
                st.write("Detected values:", len(unusual))
                st.dataframe(
                    unusual.rename("Value").to_frame(),
                    use_container_width=True
                )
            else:
                st.info(
                    "IQR is zero; this column needs special review."
                )

            fig, ax = plt.subplots()
            ax.boxplot(values)
            ax.set_title(f"Outliers: {selected}")
            st.pyplot(fig)
            plt.close(fig)

    st.caption(
        "Outliers are unusual statistical values, not necessarily errors."
    )

# ---------------- VISUAL ANALYTICS ----------------

elif page == "Visual Analytics":
    st.header("📈 Visual Analytics")

    if numeric_df.empty:
        st.info("Upload data with numerical columns to create charts.")
    else:
        selected = st.selectbox(
            "Select a numerical column",
            list(numeric_df.columns)
        )

        chart_type = st.selectbox(
            "Chart type",
            ["Histogram", "Line Chart", "Box Plot"]
        )

        values = numeric_df[selected].dropna()

        fig, ax = plt.subplots(figsize=(9, 4))

        if chart_type == "Histogram":
            ax.hist(values, bins=20)
            ax.set_ylabel("Frequency")
        elif chart_type == "Line Chart":
            ax.plot(values.reset_index(drop=True))
            ax.set_ylabel("Value")
        else:
            ax.boxplot(values)
            ax.set_ylabel("Value")

        ax.set_title(str(selected))
        ax.set_xlabel("Observation")
        st.pyplot(fig)
        plt.close(fig)

        if len(numeric_df.columns) >= 2:
            st.subheader("Correlation Matrix")
            st.dataframe(
                numeric_df.corr().round(3),
                use_container_width=True
            )

# ---------------- CLEAN & EXPORT ----------------

elif page == "Clean & Export":
    st.header("🧹 Clean & Export")

    st.write(
        "Choose cleaning options. The original uploaded data "
        "remains unchanged."
    )

    remove_dupes = st.checkbox(
        "Remove duplicate rows",
        value=True
    )

    fill_numeric = st.checkbox(
        "Fill numerical missing values with median",
        value=False
    )

    fill_category = st.checkbox(
        "Fill categorical missing values with mode",
        value=False
    )

    cleaned = df.copy()

    if remove_dupes:
        cleaned = cleaned.drop_duplicates()

    if fill_numeric:
        for col in cleaned.select_dtypes(include=np.number):
            median = cleaned[col].median()

            if pd.notna(median):
                cleaned[col] = cleaned[col].fillna(median)

    if fill_category:
        for col in cleaned.select_dtypes(
            include=["object", "category", "bool"]
        ):
            modes = cleaned[col].mode(dropna=True)

            if not modes.empty:
                cleaned[col] = cleaned[col].fillna(modes.iloc[0])

    st.metric("Original Rows", len(df))
    st.metric("Cleaned Rows", len(cleaned))
    st.metric(
        "Remaining Missing Cells",
        int(cleaned.isna().sum().sum())
    )

    st.dataframe(cleaned.head(20), use_container_width=True)

    st.download_button(
        "⬇️ Download Cleaned CSV",
        data=cleaned.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )

    report = {
        "project": "Data Detective",
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "original_rows": int(rows),
        "original_columns": int(cols),
        "missing_cells": int(missing),
        "duplicate_rows": int(duplicates),
        "quality_score": quality_score,
        "outlier_counts": outlier_counts,
        "cleaned_rows": int(len(cleaned)),
        "remaining_missing_cells": int(
            cleaned.isna().sum().sum()
        )
    }

    st.download_button(
        "⬇️ Download JSON Report",
        data=json.dumps(report, indent=4),
        file_name="investigation_report.json",
        mime="application/json"
    )

st.sidebar.divider()
st.sidebar.caption("Data Detective v2.0")
st.sidebar.caption("Built with NumPy + Pandas")
