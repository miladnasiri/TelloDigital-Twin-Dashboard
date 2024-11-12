# app.py
import streamlit as st
import asyncio
from typing import Optional, Dict
from handlers.simulation_handler import TelloBridge
from handlers.patterns import FlightPattern
from mock_data.states import TelloState
from utils.visualizer import TelloVisualizer
from analysis.state_analyzer import TelloStateAnalyzer

def init_session_state():
    """Initialize session state with all components"""
    if 'tello_state' not in st.session_state:
        st.session_state.tello_state = TelloState()
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = TelloVisualizer()
    if 'bridge' not in st.session_state:
        st.session_state.bridge = TelloBridge()
    if 'patterns' not in st.session_state:
        st.session_state.patterns = FlightPattern(st.session_state.bridge)
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = TelloStateAnalyzer()

async def handle_command(command: str, params: Optional[Dict] = None):
    """Handle async command execution with state update verification"""
    print(f"Handling command: {command} with params: {params}")  # Debug log
    
    # Store previous state
    prev_state = st.session_state.tello_state.get_state_dict()
    print(f"Previous state: {prev_state}")  # Debug log
    
    # Execute command
    result = await st.session_state.bridge.execute_command(command, params)
    print(f"Command result: {result}")  # Debug log
    
    if result and result["status"] == "success":
        # Update TelloState based on command
        if command == "move" and params:
            st.session_state.tello_state.move(params["direction"], params["distance"])
        elif command == "takeoff":
            st.session_state.tello_state.take_off()
        elif command == "land":
            st.session_state.tello_state.land()
        elif command == "rotate" and params:
            st.session_state.tello_state.rotate(params["direction"], params["angle"])
        
        # Get new state after update
        new_state = st.session_state.tello_state.get_state_dict()
        print(f"New state: {new_state}")  # Debug log
        
        # Verify state update
        if new_state != prev_state:
            # Update visualization
            st.session_state.visualizer.update(new_state)
            
            # Analyze state changes
            analysis = st.session_state.analyzer.analyze_state_change(
                prev_state, 
                new_state, 
                {'command': command, 'params': params, 'status': result["status"]}
            )
            
            # Get performance metrics
            metrics = st.session_state.analyzer.get_performance_metrics()
            
            # Add analysis results to command result
            result['analysis'] = analysis
            result['metrics'] = metrics
            
            # Predict next state
            prediction = st.session_state.analyzer.predict_next_state(
                new_state, 
                {'command': command, 'params': params}
            )
            result['predicted_next_state'] = prediction
            
        else:
            print("State did not change after command execution.")  # Debug log
    
    return result

def display_metrics(metrics: Dict):
    """Display performance metrics in a formatted way"""
    cols = st.columns(4)
    for i, (key, value) in enumerate(metrics.items()):
        with cols[i % 4]:
            st.metric(
                label=key.replace('_', ' ').title(),
                value=f"{value:.3f}"
            )

def main():
    st.set_page_config(layout="wide", page_title="Tello Digital Twin")
    init_session_state()
    
    st.title("Tello Digital Twin Dashboard")
    
    # Create main columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Control Panel")
        
        # Basic commands
        st.write("Basic Commands")
        cmd_cols = st.columns(3)
        
        if cmd_cols[0].button("Takeoff"):
            result = asyncio.run(handle_command("takeoff"))
            if result:
                st.success(f"Takeoff: {result['status']}")
                if 'analysis' in result:
                    st.write("State Changes:", result['analysis'])
        
        if cmd_cols[1].button("Land"):
            result = asyncio.run(handle_command("land"))
            if result:
                st.success(f"Landing: {result['status']}")
                if 'analysis' in result:
                    st.write("State Changes:", result['analysis'])
        
        if cmd_cols[2].button("Emergency"):
            result = asyncio.run(handle_command("emergency"))
            if result:
                st.error(f"Emergency Stop: {result['status']}")
        
        # Flight Patterns
        st.write("Flight Patterns")
        pattern_cols = st.columns(2)
        
        with st.expander("Pattern Settings"):
            size = st.slider("Pattern Size (cm)", 50, 200, 100)
            radius = st.slider("Spiral Radius (cm)", 30, 150, 50)
            height = st.slider("Pattern Height (cm)", 50, 200, 100)
        
        if pattern_cols[0].button("Square Pattern"):
            results = asyncio.run(st.session_state.patterns.square_pattern(size))
            st.success(f"Pattern completed with {len(results)} movements")
            
        if pattern_cols[1].button("Spiral Pattern"):
            results = asyncio.run(st.session_state.patterns.spiral_pattern(radius, height))
            st.success(f"Spiral completed with {len(results)} movements")
        
        # Movement control
        st.write("Movement Control")
        move_cols = st.columns(2)
        
        direction = move_cols[0].selectbox(
            "Direction",
            ["forward", "back", "left", "right", "up", "down"]
        )
        
        distance = move_cols[1].number_input(
            "Distance (cm)",
            min_value=20,
            max_value=500,
            value=100
        )
        
        if st.button("Move"):
            result = asyncio.run(handle_command("move", {
                "direction": direction,
                "distance": distance
            }))
            if result:
                st.success(f"Movement: {result['status']}")
                if 'analysis' in result:
                    st.write("State Changes:", result['analysis'])
        
        # Rotation control
        st.write("Rotation Control")
        rot_cols = st.columns(2)
        
        if rot_cols[0].button("Rotate CW"):
            result = asyncio.run(handle_command("rotate", {
                "direction": "cw",
                "angle": 90
            }))
            if result:
                st.success(f"Rotation: {result['status']}")
        
        if rot_cols[1].button("Rotate CCW"):
            result = asyncio.run(handle_command("rotate", {
                "direction": "ccw",
                "angle": 90
            }))
            if result:
                st.success(f"Rotation: {result['status']}")
    
    with col2:
        st.subheader("Drone State & Analysis")
        
        # Get current state
        state = st.session_state.tello_state.get_state_dict()
        
        # Update visualization
        st.session_state.visualizer.update(state)
        
        # Display visualization
        st.plotly_chart(st.session_state.visualizer.fig, use_container_width=True)
        
        # Analysis tabs
        tab1, tab2, tab3 = st.tabs([
            "Current Metrics", 
            "Performance Analysis",
            "Command Analysis"
        ])
        
        with tab1:
            metrics_cols = st.columns(4)
            metrics_cols[0].metric("Height (m)", f"{state['height']:.2f}")
            metrics_cols[1].metric("Battery %", f"{state['battery']}")
            metrics_cols[2].metric("Speed (km/h)", f"{state['speed']:.1f}")
            metrics_cols[3].metric("Yaw (°)", f"{state['yaw']:.1f}")
            
            pos_cols = st.columns(3)
            pos_cols[0].metric("X Position (m)", f"{state['x_pos']:.2f}")
            pos_cols[1].metric("Y Position (m)", f"{state['y_pos']:.2f}")
            pos_cols[2].metric("Status", "Flying" if state.get('is_flying', False) else "Landed")
        
        with tab2:
            if 'analyzer' in st.session_state:
                metrics = st.session_state.analyzer.get_performance_metrics()
                if metrics:
                    st.write("Performance Metrics:")
                    display_metrics(metrics)
        
        with tab3:
            if 'analyzer' in st.session_state:
                effectiveness = st.session_state.analyzer.get_command_effectiveness()
                if effectiveness:
                    st.write("Command Effectiveness:")
                    st.json(effectiveness)

if __name__ == "__main__":
    main()
