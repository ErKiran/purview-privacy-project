import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Privacy Risk Dashboard", layout="centered")

st.title("Microsoft Purview Privacy Risk Dashboard")
st.write("Before vs After Privacy Controls Analysis")

# ---------------------------------
# Read CSV Files
# ---------------------------------

before_df = pd.read_csv("before_controls.csv")
after_df = pd.read_csv("after_controls.csv")

# Combine both datasets
df = pd.concat([before_df, after_df], ignore_index=True)

# ---------------------------------
# Risk Score Calculation
# ---------------------------------

def calculate_risk_score(row):
    if row["Sensitive Files"] == 0:
        return 0

    unprotected_risk = (
        row["Unprotected Sensitive Files"] / row["Sensitive Files"]
    ) * 60

    dlp_risk = (
        row["DLP Violations"] / row["Total Files"]
    ) * 40

    return round(unprotected_risk + dlp_risk, 2)

df["Risk Score"] = df.apply(calculate_risk_score, axis=1)

# ---------------------------------
# Summary Table
# ---------------------------------

st.subheader("Privacy Metrics Summary")
st.dataframe(df, width="stretch")

# ---------------------------------
# KPI Metrics
# ---------------------------------

before_score = df.loc[df["Phase"] == "Before Controls", "Risk Score"].values[0]
after_score = df.loc[df["Phase"] == "After Controls", "Risk Score"].values[0]

col1, col2, col3 = st.columns(3)

col1.metric("Before Risk Score", before_score)
col2.metric("After Risk Score", after_score)
col3.metric("Risk Difference", round(after_score - before_score, 2))

# ---------------------------------
# Risk Score Chart
# ---------------------------------

st.subheader("Privacy Risk Score Comparison")

fig, ax = plt.subplots()

ax.bar(df["Phase"], df["Risk Score"])

ax.set_ylabel("Risk Score")
ax.set_title("Before vs After Controls")

st.pyplot(fig)

# ---------------------------------
# Sensitive Files Breakdown
# ---------------------------------

st.subheader("Sensitive File Breakdown")

fig2, ax2 = plt.subplots()

x = range(len(df))

ax2.bar(x, df["Sensitive Files"], width=0.4, label="Sensitive Files")
ax2.bar(x, df["Protected Files"], width=0.4, label="Protected Files")

ax2.set_xticks(x)
ax2.set_xticklabels(df["Phase"])

ax2.set_ylabel("File Count")
ax2.set_title("Sensitive vs Protected Files")
ax2.legend()

st.pyplot(fig2)

# ---------------------------------
# DLP Violations
# ---------------------------------

st.subheader("DLP Violations")

fig3, ax3 = plt.subplots()

ax3.bar(df["Phase"], df["DLP Violations"])

ax3.set_ylabel("Violations")
ax3.set_title("DLP Violations Comparison")

st.pyplot(fig3)

# ---------------------------------
# Final Analysis
# ---------------------------------

st.subheader("Findings and Interpretation")

st.write("""
The baseline environment initially contained limited visibility into sensitive information.
After Microsoft Purview controls were enabled, significantly more sensitive files were detected.

This increase in detections indicates improved visibility and classification capability rather than increased exposure.
""")

st.write("""
Although Microsoft Purview improved detection and policy monitoring, several sensitive files remained unprotected after controls were applied.

This demonstrates that privacy tooling improves risk visibility, but effective enforcement still depends on policy tuning, licensing availability, and operational configuration.
""")