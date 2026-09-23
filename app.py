import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nepal Rainfall Analysis", page_icon="🌧️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/nepal_rainfall.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df

df = load_data()

st.title("🌧️ Nepal Rainfall Analysis")
st.markdown("An interactive exploration of **45 years of rainfall data** across Nepal (1981–present).")
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Records", f"{len(df):,}")
c2.metric("Years", f"{df['year'].nunique()}")
c3.metric("Regions", f"{df['PCODE'].nunique()}")
c4.metric("Start Year", int(df['year'].min()))

st.markdown("---")

st.sidebar.header("Filters")
yr = st.sidebar.slider("Year Range", int(df['year'].min()), int(df['year'].max()),
                        (int(df['year'].min()), int(df['year'].max())))
regions = sorted(df['PCODE'].unique())
sel_regions = st.sidebar.multiselect("Regions", regions, default=regions[:20])

filtered = df[(df['year'] >= yr[0]) & (df['year'] <= yr[1]) & (df['PCODE'].isin(sel_regions))]

st.subheader("📅 Monthly Rainfall Pattern")
monthly = filtered.groupby('month')['rfh'].mean().reset_index()
fig1, ax1 = plt.subplots(figsize=(12, 4))
colors = ['#dc2626' if 6 <= m <= 9 else '#2563eb' for m in monthly['month']]
ax1.bar(monthly['month'], monthly['rfh'], color=colors)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
ax1.set_ylabel("Avg Rainfall (mm)")
ax1.grid(axis='y', alpha=0.3)
plt.tight_layout()
st.pyplot(fig1)

st.markdown("---")

st.subheader("📈 Yearly Rainfall Trend")
yearly = filtered.groupby('year')['rfh'].sum().reset_index()
fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.plot(yearly['year'], yearly['rfh'], marker='o', markersize=4, color='#2563eb')
if len(yearly) > 1:
    z = np.polyfit(yearly['year'], yearly['rfh'], 1)
    ax2.plot(yearly['year'], np.poly1d(z)(yearly['year']), '--', color='#dc2626',
             label=f'Trend: {z[0]:+.1f} mm/yr')
    ax2.legend()
ax2.set_ylabel("Total Rainfall (mm)")
ax2.grid(alpha=0.3)
plt.tight_layout()
st.pyplot(fig2)

st.markdown("---")

st.subheader("🗺️ Top 10 Wettest vs Driest Regions")
regional = filtered.groupby('PCODE')['rfh'].mean().sort_values(ascending=False).reset_index()
top10 = regional.head(10)
bottom10 = regional.tail(10)
combined = pd.concat([top10, bottom10])
fig3, ax3 = plt.subplots(figsize=(10, 7))
colors = ['#1e40af'] * 10 + ['#fbbf24'] * 10
ax3.barh(combined['PCODE'], combined['rfh'], color=colors)
ax3.invert_yaxis()
ax3.set_xlabel("Avg Rainfall (mm)")
ax3.grid(axis='x', alpha=0.3)
plt.tight_layout()
st.pyplot(fig3)

st.markdown("---")

with st.expander("🔍 View raw data"):
    st.dataframe(filtered.head(500))

st.caption("Data: [HDX Nepal Rainfall](https://data.humdata.org/dataset/npl-rainfall-subnational)")