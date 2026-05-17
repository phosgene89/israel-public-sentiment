import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="Time Series + Forecast", layout="wide")
st.title("📈 Time Series Explorer with Forecast")
st.markdown("**AvgTone** Historical + 5-Step Forecast (Connected)")

# ====================== HISTORICAL DATA ======================
raw_hist = """time_step,AvgTone,NumMentions,GoldsteinScale
46139,-5.167173,10.0,4.000000
46140,-3.685762,190.0,3.565000
46141,-2.204350,370.0,3.130000
46142,-4.052501,331.0,3.502222
46143,-14.871795,25.0,-7.000000"""

df_hist = pd.read_csv(StringIO(raw_hist))
df_hist['time_step'] = pd.to_numeric(df_hist['time_step'])

last_hist = df_hist.iloc[-1]

# ====================== DUMMY FORECAST ======================
data_pred = {
    'time_step': [46144, 46145, 46146, 46147, 46148],
    'AvgTone': [-6.85, -5.23, -4.71, -7.12, -3.95],
    'prediction_lower': [-9.12, -8.10, -8.45, -11.80, -9.20],
    'prediction_upper': [-4.58, -2.36, -0.97, -2.44, 1.30],
    'forecast_step': [1, 2, 3, 4, 5]
}

df_pred = pd.DataFrame(data_pred)

# ====================== CONNECTED FORECAST LINE ======================
df_forecast_line = pd.DataFrame({
    'time_step': [last_hist['time_step']] + df_pred['time_step'].tolist(),
    'AvgTone': [last_hist['AvgTone']] + df_pred['AvgTone'].tolist()
})

# ====================== CONNECTED CONFIDENCE INTERVAL ======================
# Start with zero width at last historical point
df_conf = pd.concat([
    pd.DataFrame({
        'time_step': [last_hist['time_step']],
        'lower': [last_hist['AvgTone']],
        'upper': [last_hist['AvgTone']]
    }),
    pd.DataFrame({
        'time_step': df_pred['time_step'],
        'lower': df_pred['prediction_lower'],
        'upper': df_pred['prediction_upper']
    })
], ignore_index=True)

# ====================== PLOTTING ======================
fig = go.Figure()

# Historical
fig.add_trace(go.Scatter(
    x=df_hist['time_step'],
    y=df_hist['AvgTone'],
    mode='lines+markers',
    name='Historical',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=8)
))

# Forecast Line (connected)
fig.add_trace(go.Scatter(
    x=df_forecast_line['time_step'],
    y=df_forecast_line['AvgTone'],
    mode='lines+markers',
    name='Forecast',
    line=dict(color='#ff7f0e', width=4, dash='dash'),
    marker=dict(size=9, symbol='diamond')
))

# Confidence Interval (starts with zero width at last point)
fig.add_trace(go.Scatter(
    x=pd.concat([df_conf['time_step'], df_conf['time_step'][::-1]]),
    y=pd.concat([df_conf['upper'], df_conf['lower'][::-1]]),
    fill='toself',
    fillcolor='rgba(255, 127, 14, 0.25)',
    line=dict(color='rgba(255,127,14,0)'),
    name='95% Confidence Interval'
))

fig.update_layout(
    title="AvgTone Time Series + 5-Step Forecast (Smooth Connection)",
    xaxis_title="Time Step",
    yaxis_title="AvgTone",
    height=650,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# ====================== METRICS ======================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Last Actual AvgTone", f"{last_hist['AvgTone']:.3f}")
with col2:
    st.metric("5-Step Forecast", f"{df_pred['AvgTone'].iloc[-1]:.3f}")
with col3:
    change = ((df_pred['AvgTone'].iloc[-1] - last_hist['AvgTone']) / abs(last_hist['AvgTone']) * 100)
    st.metric("Expected Change", f"{change:+.1f}%")

# Data Tables
tab1, tab2 = st.tabs(["📊 Historical Data", "🔮 Forecast Data"])
with tab1:
    st.dataframe(df_hist, use_container_width=True)
with tab2:
    st.dataframe(df_pred, use_container_width=True)

st.caption("The forecast line and confidence band now start smoothly from the last historical point with zero uncertainty at that point.")