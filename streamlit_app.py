import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="Time Series + Forecast", layout="wide")
st.title("📈 Time Series Explorer with Forecast")
st.markdown("**AvgTone** Historical + 5-Step Forecast")

# ====================== HISTORICAL DATA ======================
st.sidebar.header("Data Input")

raw_hist = """time_step,AvgTone,NumMentions,GoldsteinScale
46139,-5.167173,10.0,4.000000
46140,-3.685762,190.0,3.565000
46141,-2.204350,370.0,3.130000
46142,-4.052501,331.0,3.502222
46143,-14.871795,25.0,-7.000000"""

df_hist = pd.read_csv(StringIO(raw_hist))
df_hist['time_step'] = pd.to_numeric(df_hist['time_step'])

st.success(f"Historical data loaded: {len(df_hist)} rows")

# ====================== DUMMY FORECAST DATAFRAME ======================
# This simulates what your Databricks endpoint would return
data_pred = {
    'time_step': [46144, 46145, 46146, 46147, 46148],
    'AvgTone': [-6.85, -5.23, -4.71, -7.12, -3.95],           # Main prediction
    'prediction_lower': [-9.12, -8.10, -8.45, -11.80, -9.20],
    'prediction_upper': [-4.58, -2.36, -0.97, -2.44, 1.30],
    'forecast_step': [1, 2, 3, 4, 5],
    'prediction_timestamp': ['2026-05-18 06:30'] * 5
}

df_pred = pd.DataFrame(data_pred)

st.sidebar.subheader("Forecast Info")
st.sidebar.write(f"**5-Step Forecast** generated")
st.sidebar.write(f"Last time_step: {df_hist['time_step'].max()}")

# ====================== MAIN PLOT ======================
fig = go.Figure()

# Historical Data
fig.add_trace(go.Scatter(
    x=df_hist['time_step'],
    y=df_hist['AvgTone'],
    mode='lines+markers',
    name='Historical AvgTone',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=8)
))

# Forecast
fig.add_trace(go.Scatter(
    x=df_pred['time_step'],
    y=df_pred['AvgTone'],
    mode='lines+markers',
    name='Forecast (5 steps)',
    line=dict(color='#ff7f0e', width=4, dash='dash'),
    marker=dict(size=9, symbol='diamond')
))

# Confidence Interval
fig.add_trace(go.Scatter(
    x=pd.concat([df_pred['time_step'], df_pred['time_step'][::-1]]),
    y=pd.concat([df_pred['prediction_upper'], df_pred['prediction_lower'][::-1]]),
    fill='toself',
    fillcolor='rgba(255, 127, 14, 0.25)',
    line=dict(color='rgba(255,127,14,0)'),
    name='95% Confidence Interval'
))

fig.update_layout(
    title="AvgTone Time Series + 5-Step Forecast",
    xaxis_title="Time Step",
    yaxis_title="AvgTone",
    height=650,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# ====================== METRICS ======================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Last Actual", f"{df_hist['AvgTone'].iloc[-1]:.3f}")
with col2:
    st.metric("5-Step Forecast", f"{df_pred['AvgTone'].iloc[-1]:.3f}")
with col3:
    change = ((df_pred['AvgTone'].iloc[-1] - df_hist['AvgTone'].iloc[-1]) / 
              abs(df_hist['AvgTone'].iloc[-1]) * 100)
    st.metric("Expected Change", f"{change:+.1f}%")
with col4:
    st.metric("Forecast Horizon", "5 steps")

# ====================== DATA TABLES ======================
tab1, tab2 = st.tabs(["Historical Data", "Forecast Data"])

with tab1:
    st.dataframe(df_hist, use_container_width=True)

with tab2:
    st.dataframe(df_pred, use_container_width=True)

# Optional: Show all columns side by side
st.subheader("Full Combined View")
combined = pd.concat([
    df_hist.assign(type='Historical'),
    df_pred.assign(type='Forecast').drop(columns=['prediction_timestamp'])
], ignore_index=True)
st.dataframe(combined, use_container_width=True)

st.caption("✅ This structure is ready to be replaced with real predictions from your Databricks endpoint.")