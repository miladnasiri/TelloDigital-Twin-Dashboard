
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

class TelloVisualizer:
    def __init__(self):
        # Create plotly figure with subplots
        self.fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "scene", "rowspan": 2}, {"type": "indicator"}],
                [None, {"type": "indicator"}]
            ],
            subplot_titles=('Drone Position (Live)', 'Battery Level', 'Height')
        )
        
        # Store trajectory points
        self.trajectory_x = []
        self.trajectory_y = []
        self.trajectory_z = []
        
        self._setup_plot()
        
    def _setup_plot(self):
        # 3D position plot
        self.fig.add_trace(
            go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode='markers+text',
                marker=dict(
                    size=15,
                    color='red',
                    symbol='circle'
                ),
                text=['Drone'],
                name='Current Position',
                showlegend=True
            ),
            row=1, col=1
        )
        
        # Add trajectory line
        self.fig.add_trace(
            go.Scatter3d(
                x=self.trajectory_x,
                y=self.trajectory_y,
                z=self.trajectory_z,
                mode='lines',
                line=dict(color='blue', width=3),
                name='Flight Path'
            ),
            row=1, col=1
        )
        
        # Add direction vector
        self.fig.add_trace(
            go.Scatter3d(
                x=[0, 1],
                y=[0, 0],
                z=[0, 0],
                mode='lines',
                line=dict(color='green', width=2),
                name='Direction'
            ),
            row=1, col=1
        )
        
        # Battery indicator
        self.fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=100,
                title={'text': "Battery %"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'steps': [
                        {'range': [0, 20], 'color': "red"},
                        {'range': [20, 50], 'color': "yellow"},
                        {'range': [50, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 20
                    }
                }
            ),
            row=1, col=2
        )
        
        # Height indicator
        self.fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=0,
                title={'text': "Height (m)"},
                gauge={
                    'axis': {'range': [0, 10]},
                    'bar': {'color': "royalblue"},
                    'steps': [
                        {'range': [0, 1], 'color': "lightgray"},
                        {'range': [1, 5], 'color': "gray"}
                    ],
                }
            ),
            row=2, col=2
        )
        
        # Update layout
        self.fig.update_layout(
            height=800,
            showlegend=True,
            scene=dict(
                xaxis_title='X Position (m)',
                yaxis_title='Y Position (m)',
                zaxis_title='Height (m)',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            )
        )
    
    def update(self, state):
        """Update visualization with new state"""
        print(f"Updating visualization with state: {state}")  # Debug log
        
        # Update 3D position
        if 'x_pos' in state and 'y_pos' in state and 'height' in state:
            self.trajectory_x.append(state['x_pos'])
            self.trajectory_y.append(state['y_pos'])
            self.trajectory_z.append(state['height'])
            
            print(f"Updated position: x={state['x_pos']}, y={state['y_pos']}, z={state['height']}")  # Debug log
            
            # Update drone position
            self.fig.update_traces(
                x=[state['x_pos']],
                y=[state['y_pos']],
                z=[state['height']],
                selector=dict(mode='markers+text')
            )
            
            # Update trajectory
            self.fig.update_traces(
                x=self.trajectory_x,
                y=self.trajectory_y,
                z=self.trajectory_z,
                selector=dict(mode='lines')
            )
        
        # Update direction vector based on yaw
        if 'yaw' in state:
            yaw_rad = np.radians(state['yaw'])
            dir_x = np.cos(yaw_rad)
            dir_y = np.sin(yaw_rad)
            
            self.fig.update_traces(
                x=[state['x_pos'], state['x_pos'] + dir_x],
                y=[state['y_pos'], state['y_pos'] + dir_y],
                z=[state['height'], state['height']],
                selector=dict(name='Direction')
            )
        
        # Update battery indicator
        if 'battery' in state:
            self.fig.update_traces(
                value=state['battery'],
                selector=dict(title={'text': "Battery %"})
            )
        
        # Update height indicator
        if 'height' in state:
            self.fig.update_traces(
                value=state['height'],
                selector=dict(title={'text': "Height (m)"})
            )

        print("Visualization update complete")  # Debug log
