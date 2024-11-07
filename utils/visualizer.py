import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TelloVisualizer:
    def __init__(self):
        self.fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"type": "scene", "rowspan": 2}, {"type": "indicator"}],
                  [None, {"type": "indicator"}]],
            subplot_titles=("Tello Position", "Battery Level", "Height")
        )
        self._setup_plot()
        
    def _setup_plot(self):
        self.fig.add_trace(
            go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode="markers+text",
                marker=dict(size=10, color="red"),
                text=["Drone"],
                name="Current Position"
            ),
            row=1, col=1
        )
        
        self.fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=100,
                title={"text": "Battery %"},
                gauge={"axis": {"range": [0, 100]},
                       "steps": [
                           {"range": [0, 20], "color": "red"},
                           {"range": [20, 50], "color": "yellow"},
                           {"range": [50, 100], "color": "green"}
                       ]}
            ),
            row=1, col=2
        )
        
        self.fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=0,
                title={"text": "Height (m)"},
                gauge={"axis": {"range": [0, 10]}}
            ),
            row=2, col=2
        )
        
        self.fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Tello Digital Twin Visualization"
        )
        
    def update(self, state):
        self.fig.update_traces(
            x=[state["x_pos"]],
            y=[state["y_pos"]],
            z=[state["height"]],
            selector=dict(type="scatter3d")
        )
        
        self.fig.update_traces(
            value=state["battery"],
            selector=dict(type="indicator", title={"text": "Battery %"})
        )
        
        self.fig.update_traces(
            value=state["height"],
            selector=dict(type="indicator", title={"text": "Height (m"})
        )
