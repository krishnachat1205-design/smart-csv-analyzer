# ============================================================
# Smart CSV Analyzer Pro
# Upload a CSV, run analysis, and explore an interactive dashboard
# ============================================================

# --- Import libraries ---
# streamlit: builds the web app (buttons, charts, file upload)
# pandas: reads and analyzes CSV data (tables, rows, columns)
import streamlit as st
import pandas as pd

# --- Page setup ---
st.set_page_config(page_title="Smart CSV Analyzer Pro", page_icon="📊", layout="wide")

st.title("📊 Smart CSV Analyzer Pro")
st.write("Upload a CSV file for automatic analysis and an interactive dashboard.")

# --- File upload ---
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:

    # --- Read the CSV ---
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read this file. Please upload a valid CSV.\n\nError: {e}")
        st.stop()

    st.success("File loaded successfully!")

    # --- Core metrics (used in analysis, report, and dashboard) ---
    row_count = len(df)
    column_count = len(df.columns)
    missing_counts = df.isnull().sum()
    total_missing_cells = int(missing_counts.sum())
    duplicate_count = int(df.duplicated().sum())

    # --- Auto-detect column types ---
    # Numeric columns: numbers (integers, decimals)
    numeric_df = df.select_dtypes(include="number")
    numeric_columns = list(numeric_df.columns)

    # Categorical columns: text and other non-number columns
    categorical_df = df.select_dtypes(exclude="number")
    categorical_columns = list(categorical_df.columns)

    # --- Dataset Health Score (out of 100) ---
    total_cells = row_count * column_count
    missing_ratio = total_missing_cells / total_cells if total_cells > 0 else 0
    duplicate_ratio = duplicate_count / row_count if row_count > 0 else 0

    health_score = 100
    health_score -= missing_ratio * 50
    health_score -= duplicate_ratio * 50
    health_score = max(0, min(100, round(health_score)))

    # ============================================================
    # ANALYSIS SECTION
    # Text tables and summaries (same as before, no extra clicks)
    # ============================================================
    st.header("Analysis")

    st.subheader("First 10 rows")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Column names")
    for name in df.columns:
        st.write(f"- {name}")

    st.subheader("Data types per column")
    dtype_table = pd.DataFrame({
        "Column": df.columns,
        "Data type": df.dtypes.astype(str).values,
    })
    st.dataframe(dtype_table, use_container_width=True)

    st.subheader("Missing values per column")
    missing_table = pd.DataFrame({
        "Column": missing_counts.index,
        "Missing values": missing_counts.values,
    })
    st.dataframe(missing_table, use_container_width=True)

    st.subheader("Numeric column statistics")
    if len(numeric_columns) == 0:
        st.write("This file has no numeric columns to summarize.")
        stats_table = pd.DataFrame()
    else:
        stats_rows = []
        for col_name in numeric_columns:
            stats_rows.append({
                "Column": col_name,
                "count": numeric_df[col_name].count(),
                "mean": numeric_df[col_name].mean(),
                "median": numeric_df[col_name].median(),
                "minimum": numeric_df[col_name].min(),
                "maximum": numeric_df[col_name].max(),
                "standard deviation": numeric_df[col_name].std(),
            })
        stats_table = pd.DataFrame(stats_rows)
        st.dataframe(stats_table, use_container_width=True)

    st.subheader("Download report")
    st.write("Save a text summary of this analysis:")

    def table_to_text(table, title):
        if table is None or len(table) == 0:
            return f"{title}\n(none)\n\n"
        return f"{title}\n{table.to_string(index=False)}\n\n"

    report_lines = [
        "SMART CSV ANALYZER PRO - ANALYSIS REPORT",
        "=" * 40,
        f"File name: {uploaded_file.name}",
        "",
        "DATASET HEALTH SCORE",
        f"Score: {health_score} / 100",
        f"Total missing cells: {total_missing_cells}",
        f"Duplicate rows: {duplicate_count}",
        "",
        "DATASET SIZE",
        f"Total rows: {row_count}",
        f"Total columns: {column_count}",
        "",
        "COLUMN NAMES",
    ]
    for name in df.columns:
        report_lines.append(f"  - {name}")
    report_lines.append("")

    report_text = "\n".join(report_lines)
    report_text += table_to_text(dtype_table, "DATA TYPES PER COLUMN")
    report_text += table_to_text(missing_table, "MISSING VALUES PER COLUMN")
    report_text += "\nDUPLICATE ROWS\n"
    report_text += f"Duplicate row count: {duplicate_count}\n\n"
    report_text += table_to_text(stats_table, "NUMERIC COLUMN STATISTICS")

    st.download_button(
        label="Download Analysis Report",
        data=report_text,
        file_name="csv_analysis_report.txt",
        mime="text/plain",
    )

    # ============================================================
    # INTERACTIVE DASHBOARD
    # Charts and KPI cards — everything runs automatically after upload
    # ============================================================
    st.divider()
    st.header("Interactive Dashboard")

    # --- KPI cards ---
    # st.metric shows a big number with a label (like a dashboard tile)
    st.subheader("Key metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.metric("Total Rows", row_count)
    with kpi2:
        st.metric("Total Columns", column_count)
    with kpi3:
        st.metric("Missing Values", total_missing_cells)
    with kpi4:
        st.metric("Duplicate Rows", duplicate_count)
    with kpi5:
        st.metric("Dataset Health Score", f"{health_score} / 100")

    # --- Missing values chart ---
    # Bar height = how many empty cells each column has
    st.subheader("Missing values chart")
    if total_missing_cells == 0:
        st.write("No missing values — great job!")
    else:
        missing_chart_data = missing_counts[missing_counts > 0].to_frame(name="Missing count")
        st.bar_chart(missing_chart_data, use_container_width=True)

    # --- Histograms for numeric columns ---
    st.subheader("Numeric column histograms")
    if len(numeric_columns) == 0:
        st.write("No numeric columns found for histograms.")
    else:
        st.caption(f"Detected numeric columns: {', '.join(numeric_columns)}")
        for col_name in numeric_columns:
            st.write(f"**{col_name}**")
            series = numeric_df[col_name].dropna()

            # Few unique values: chart each value directly
            # Many values: group into 10 bins (ranges) so the chart stays readable
            if series.nunique() <= 15:
                hist_data = series.value_counts().sort_index().to_frame(name="Count")
            else:
                binned = pd.cut(series, bins=10)
                hist_data = binned.value_counts().sort_index()
                hist_data.index = hist_data.index.astype(str)
                hist_data = hist_data.to_frame(name="Count")

            st.bar_chart(hist_data, use_container_width=True)

    # --- Bar charts for categorical columns (top values) ---
    st.subheader("Categorical column bar charts")
    if len(categorical_columns) == 0:
        st.write("No categorical (text) columns found for bar charts.")
    else:
        st.caption(f"Detected categorical columns: {', '.join(categorical_columns)}")
        for col_name in categorical_columns:
            st.write(f"**{col_name}** (top 10 values)")
            # value_counts() counts how often each category appears
            top_values = categorical_df[col_name].value_counts().head(10)
            top_chart_data = top_values.to_frame(name="Count")
            st.bar_chart(top_chart_data, use_container_width=True)

    # --- Correlation matrix for numeric columns ---
    # Shows how pairs of numeric columns move together (-1 to +1)
    st.subheader("Correlation matrix (numeric columns)")
    if len(numeric_columns) < 2:
        st.write("Need at least 2 numeric columns to build a correlation matrix.")
    else:
        correlation_matrix = numeric_df.corr()
        st.dataframe(correlation_matrix, use_container_width=True)
        st.caption(
            "Values close to 1 or -1 mean stronger relationships. "
            "Values near 0 mean little or no linear relationship."
        )

else:
    st.info("👆 Upload a CSV file above to get started.")
