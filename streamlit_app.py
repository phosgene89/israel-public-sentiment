import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="Time Series Explorer", layout="wide")
st.title("📈 Time Series Data Explorer")
st.markdown("Paste your data below or use the example")

# ====================== DATA INPUT ======================
st.sidebar.header("Data Input")

data_input = st.sidebar.radio("Choose input method", ["Use Example Data", "Paste CSV Data"])

if data_input == "Use Example Data":
    raw_data = """time_step,AvgTone,NumMentions,GoldsteinScale,Actor1Geo_Lat,Actor1Geo_Long
46139,-5.167173,10.0,4.000000,31.50000,34.75000
46140,-3.685762,190.0,3.565000,31.52667,34.79833
46141,-2.204350,370.0,3.130000,31.55334,34.84666
46142,-4.052501,331.0,3.502222,31.38808,39.33436
46143,-14.871795,25.0,-7.000000,31.96420,34.80440"""
else:
    raw_data = st.sidebar.text_area("Paste your CSV data here", height=200)

# Parse the data
try:
    df = pd.read_csv(StringIO(raw_data.strip()))
    
    # Convert time_step to datetime (assuming format like 46139 = 2046-01-39? → we'll treat as date)
    if 'time_step' in df.columns:
        df['Date'] = pd.to_datetime(df['time_step'].astype(str).str.zfill(6), 
                                   format='%y%m%d', errors='coerce')
    else:
        st.error("Data must contain a 'time_step' column")
        st.stop()

    st.success(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
    
except Exception as e:
    st.error(f"Error parsing data: {e}")
    st.stop()

# ====================== DISPLAY ======================
st.subheader("Data Preview")
st.dataframe(df, use_container_width=True)

# Select columns to plot
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
if 'time_step' in numeric_cols:
    numeric_cols.remove('time_step')
if 'Date' in numeric_cols:
    numeric_cols.remove('Date')

plot_columns = st.multiselect("Select columns to plot", 
                             options=numeric_cols, 
                             default=['GoldsteinScale', 'NumMentions'])

# ====================== PLOTTING ======================
if plot_columns:
    fig = go.Figure()
    
    for col in plot_columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df[col],
            mode='lines+markers',
            name=col,
            line=dict(width=3),
            marker=dict(size=6)
        ))

    fig.update_layout(
        title="Time Series Plot",
        xaxis_title="Date",
        yaxis_title="Value",
        height=650,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Optional: Individual plots
    if len(plot_columns) > 1:
        st.subheader("Individual Plots")
        cols = st.columns(2)
        for i, col in enumerate(plot_columns):
            with cols[i % 2]:
                fig_single = go.Figure()
                fig_single.add_trace(go.Scatter(
                    x=df['Date'], y=df[col], mode='lines+markers', name=col
                ))
                fig_single.update_layout(title=col, height=400)
                st.plotly_chart(fig_single, use_container_width=True)
else:
    st.warning("Please select at least one column to plot.")

st.caption("Tip: You can paste new data in the sidebar. The app will automatically detect numeric columns and plot them.")