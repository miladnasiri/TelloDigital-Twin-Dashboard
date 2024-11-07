import streamlit as st
from mock_data.states import TelloState
from utils.visualizer import TelloVisualizer
import time

def main():
    st.set_page_config(layout="wide", page_title="Tello Digital Twin")
    
    if 'tello_state' not in st.session_state:
        st.session_state.tello_state = TelloState()
        st.session_state.visualizer = TelloVisualizer()
    
    tello = st.session_state.tello_state
    viz = st.session_state.visualizer
    
    st.title("Tello Digital Twin Dashboard")
    
    # Create main columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Control Panel")
        
        # Basic commands
        st.write("Basic Commands")
        cmd_cols = st.columns(4)
        
        if cmd_cols[0].button("Takeoff"):
            tello.take_off()
        
        if cmd_cols[1].button("Land"):
            tello.land()
        
        if cmd_cols[2].button("Emergency"):
            tello.land()
        
        # Height control
        st.write("Height Control")
        height = st.slider("Target Height (m)", 0.3, 10.0, 1.0, 0.1)
        if st.button("Set Height"):
            tello.set_height(height)
        
        # Movement control
        st.write("Movement Control")
        move_cols = st.columns(2)
        
        direction = move_cols[0].selectbox(
            "Direction",
            ["forward", "back", "left", "right"]
        )
        
        distance = move_cols[1].number_input(
            "Distance (cm)",
            min_value=20,
            max_value=500,
            value=100
        )
        
        if st.button("Move"):
            tello.move(direction, distance)
    
    with col2:
        st.subheader("Drone State")
        
        # Get current state
        state = tello.get_state_dict()
        
        # Update visualization
        viz.update(state)
        
        # Display the plot
        st.plotly_chart(viz.fig, use_container_width=True)
        
        # Display metrics - Fixed string formatting
        metrics_cols = st.columns(3)
        height_str = f"{state['height']:.2f}"
        battery_str = f"{state['battery']}"
        speed_str = f"{state['speed']:.1f}"
        
        metrics_cols[0].metric("Height (m)", height_str)
        metrics_cols[1].metric("Battery %", battery_str)
        metrics_cols[2].metric("Speed (km/h)", speed_str)

if __name__ == "__main__":
    main()
