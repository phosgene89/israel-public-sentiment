import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="Time Series Explorer", layout="wide")
st.title("📈 Time Series Data Explorer")
st.markdown("Plots using **time_step** as the time axis")

# ====================== DATA INPUT ======================
st.sidebar.header("Data Input")

data_input = st.sidebar.radio("Choose input method", ["Use Example Data", "Paste Your Data"])

if data_input == "Use Example Data":
    raw_data = """time_step,AvgTone,NumMentions,GoldsteinScale,Actor1Geo_Lat,Actor1Geo_Long
46139,-5.167173,10.0,4.000000,31.50000,34.75000
46140,-3.685762,190.0,3.565000,31.52667,34.79833
46141,-2.204350,370.0,3.130000,31.55334,34.84666
46142,-4.052501,331.0,3.502222,31.38808,39.33436
46143,-14.871795,25.0,-7.000000,31.96420,34.80440"""
else:
    raw_data = st.sidebar.text_area("Paste your CSV data here", height=250)

# Parse data
try:
    df = pd.read_csv(StringIO(raw_data.strip()))
    
    if 'time_step' not in df.columns:
        st.error("Data must contain a 'time_step' column")
        st.stop()
    
    # Ensure time_step is numeric
    df['time_step'] = pd.to_numeric(df['time_step'], errors='coerce')
    df = df.sort_values('time_step').reset_index(drop=True)
    
    st.success(f"✅ Loaded {len(df)} rows | Time steps from {df['time_step'].min()} to {df['time_step'].max()}")
    
except Exception as e:
    st.error(f"Error parsing data: {e}")
    st.stop()

# ====================== PREVIEW ======================
st.subheader("Data Preview")
st.dataframe(df, use_container_width=True)

# Select columns to plot
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
numeric_cols.remove('time_step')  # Remove time_step from y-axis options

plot_columns = st.multiselect(
    "Select columns to plot", 
    options=numeric_cols, 
    default=['GoldsteinScale', 'NumMentions']
)

# ====================== MAIN TIME SERIES PLOT ======================
if plot_columns:
    fig = go.Figure()
    
    for col in plot_columns:
        fig.add_trace(go.Scatter(
            x=df['time_step'],
            y=df[col],
            mode='lines+markers',
            name=col,
            line=dict(width=3),
            marker=dict(size=7)
        ))

    fig.update_layout(
        title="Time Series Plot (using time_step)",
        xaxis_title="Time Step",
        yaxis_title="Value",
        height=650,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show individual plots if multiple columns selected
    if len(plot_columns) > 1:
        st.subheader("Individual Time Series")
        cols_grid = st.columns(2)
        for i, col in enumerate(plot_columns):
            with cols_grid[i % 2]:
                fig_i = go.Figure()
                fig_i.add_trace(go.Scatter(
                    x=df['time_step'], 
                    y=df[col], 
                    mode='lines+markers',
                    name=col,
                    line=dict(width=3)
                ))
                fig_i.update_layout(
                    title=col,
                    xaxis_title="Time Step",
                    height=400
                )
                st.plotly_chart(fig_i, use_container_width=True)

else:
    st.info("Please select at least one column to plot.")

st.caption("💡 **time_step** is used directly as the x-axis for accurate time series representation.")