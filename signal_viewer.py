import streamlit as st
import numpy as np
import plotly.graph_objs as go
import json
import datetime
import pandas as pd

# Function to convert seconds to Plotly date format
def seconds_to_datetime(seconds):
    # Reference date for the Plotly date format
    ref_date = datetime.datetime(2024, 1, 1)
    # Calculate the actual datetime
    actual_time = ref_date + datetime.timedelta(seconds=seconds)
    # return actual_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    return actual_time.strftime('%Y-%m-%d %H:%M:%S.%f')

def seconds_to_hm(seconds):
    # Calculate hours
    hours = seconds // 3600
    seconds %= 3600
    
    # Calculate minutes
    minutes = seconds // 60
    seconds %= 60
    
    # Calculate whole seconds and milliseconds
    whole_seconds = int(seconds)
    milliseconds = int((seconds - whole_seconds) * 1000)
    
    # Format the result as h:m:s:ms
    formatted_time = f"{int(hours):01}:{int(minutes):02}"
    
    return formatted_time

# Function to convert seconds to h:m:s format
def seconds_to_hms(seconds):
    return str(datetime.timedelta(seconds=seconds))

# Streamlit setup
st.set_page_config(layout="wide",page_title='Signal Viewer',page_icon='./ecg.png')
st.image('./Icons/signal_icon.png',width=150,output_format='PNG')
st.title('Signal Viewer')

events_df = pd.DataFrame()

# Creating columns for layout
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.write('Upload three files: one for signal values (NumPy array), one for time values (NumPy array), and one for events (JSON).')
    
    # Uploading the NumPy arrays and JSON file
    uploaded_file_signal = st.file_uploader("Choose the signal values NumPy file", type="npy")
    uploaded_file_time = st.file_uploader("Choose the time values NumPy file", type="npy")
    uploaded_file_events = st.file_uploader("Choose the events JSON file", type="json")

if uploaded_file_signal is not None and uploaded_file_time is not None:
    # Load the NumPy arrays
    signal_values = np.load(uploaded_file_signal)
    time_values = np.load(uploaded_file_time)
    
    # Transform the time values to Plotly date format
    time_values_datetime = [seconds_to_datetime(sec) for sec in time_values]

    with col2:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=time_values_datetime, y=signal_values, mode='lines', name='Signal'))

        # If events file is uploaded, add event markers
        events_data = []
        if uploaded_file_events is not None:
            events = json.load(uploaded_file_events)
            for event in events:
                index, event_time, event_text, event_time_str = event
                event_time_datetime = seconds_to_datetime(event_time)
                event_time_hms = seconds_to_hm(event_time)
                events_data.append({"Event": event_text, "Time": event_time_hms})
                fig.add_trace(go.Scatter(
                    x=[event_time_datetime, event_time_datetime],
                    y=[min(signal_values), max(signal_values)],
                    mode='lines+text',
                    name=event_text,
                    text=[event_text, ""],
                    textposition='top right',
                    line=dict(color='red', dash='dash'),
                ))
            
            # Convert events data to a dataframe
            events_df = pd.DataFrame(events_data)

        # updated layout with formatted x-axis ticks
        fig.update_layout(
            title='Signal Viewer',
            xaxis=dict(
                title='Time',
                tickformat='%H:%M:%S',  # Using tickformat for h:m:s with milliseconds format
                tickmode='auto'
            ),
            yaxis=dict(
                title='Value'
            ),
            width=1000,
            height=600,
        )

        # Display the plot
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        
    with col3:
        # Display the events table
        st.header("Events")
        st.dataframe(events_df, height=600, hide_index=True)  # Adjusted height for 10-12 lines
