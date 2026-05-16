import streamlit as st

st.title("🎈 My new app")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Time Series Predictor",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Time Series Predictions")
st.markdown("Simple interactive demo showing historical data + future predictions")

# Sidebar controls
st.sidebar.header("Controls")

# Data selection
dataset = st.sidebar.selectbox(
    "Select Dataset",
    ["Daily Sales", "Website Traffic", "Stock Price", "Temperature"]
)

forecast_days = st.sidebar.slider("Forecast Horizon (days)", 7, 60, 30)
show_confidence = st.sidebar.checkbox("Show Confidence Interval", value=True)

# Generate synthetic data
def generate_data(dataset_name):
    np.random.seed(42)
    today = datetime.now()
    dates = [today - timedelta(days=i) for i in range(120, -1, -1)]
    
    if dataset_name == "Daily Sales":
        values = np.cumsum(np.random.normal(10, 5, 121)) + 500
        unit = "Sales ($)"
    elif dataset_name == "Website Traffic":
        values = np.cumsum(np.random.normal(8, 15, 121)) + 1200
        unit = "Visitors"
    elif dataset_name == "Stock Price":
        values = 150 + np.cumsum(np.random.normal(0.2, 1.5, 121))
        unit = "Price ($)"
    else:  # Temperature
        values = 22 + np.sin(np.arange(121)/10) * 8 + np.random.normal(0, 2, 121)
        unit = "°C"
    
    df = pd.DataFrame({"Date": dates, "Actual": values.round(2)})
    df.set_index("Date", inplace=True)
    return df, unit

# Generate data
df, unit = generate_data(dataset)

# Create fake predictions
last_date = df.index[-1]
future_dates = [last_date + timedelta(days=i) for i in range(1, forecast_days + 1)]

# Simple trend + noise forecast
last_value = df["Actual"].iloc[-1]
trend = np.linspace(last_value, last_value * 1.15, forecast_days)
noise = np.random.normal(0, last_value * 0.03, forecast_days)
predictions = trend + noise

pred_df = pd.DataFrame({
    "Date": future_dates,
    "Prediction": predictions.round(2)
}).set_index("Date")

# Plot
fig = go.Figure()

# Historical data
fig.add_trace(go.Scatter(
    x=df.index, 
    y=df["Actual"],
    mode='lines+markers',
    name='Historical',
    line=dict(color='#1f77b4', width=2)
))

# Predictions
fig.add_trace(go.Scatter(
    x=pred_df.index,
    y=pred_df["Prediction"],
    mode='lines+markers',
    name='Prediction',
    line=dict(color='#ff7f0e', width=3, dash='dash')
))

if show_confidence:
    upper = pred_df["Prediction"] * 1.12
    lower = pred_df["Prediction"] * 0.88
    fig.add_trace(go.Scatter(
        x=pred_df.index.tolist() + pred_df.index.tolist()[::-1],
        y=upper.tolist() + lower.tolist()[::-1],
        fill='toself',
        fillcolor='rgba(255, 127, 14, 0.2)',
        line=dict(color='rgba(255,127,14,0)'),
        name='Confidence Interval'
    ))

fig.update_layout(
    title=f"{dataset} - Historical + {forecast_days}-Day Forecast",
    xaxis_title="Date",
    yaxis_title=unit,
    hovermode="x unified",
    height=600,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Last Actual Value", f"{df['Actual'].iloc[-1]:.2f} {unit}")
with col2:
    st.metric("Predicted Value (30 days)", f"{pred_df['Prediction'].iloc[-1]:.2f} {unit}")
with col3:
    st.metric("Expected Change", f"{((pred_df['Prediction'].iloc[-1] / df['Actual'].iloc[-1]) - 1)*100:.1f}%")

# Data tables
tab1, tab2 = st.tabs(["Historical Data", "Predictions"])

with tab1:
    st.dataframe(df.tail(15), use_container_width=True)

with tab2:
    st.dataframe(pred_df.head(20), use_container_width=True)

st.caption("📌 This is a demo app using synthetic data. In a real app, you would connect to your model (Prophet, LSTM, etc.).")
