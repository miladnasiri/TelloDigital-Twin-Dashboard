import numpy as np
import pandas as pd
from typing import Dict
from datetime import datetime

class TelloStateAnalyzer:
    def __init__(self):
        self.state_history = pd.DataFrame()
        self.command_history = pd.DataFrame()
        self.divergence_metrics = pd.DataFrame()
        
    def analyze_state_change(self, prev_state: Dict, new_state: Dict, command: Dict) -> Dict:
        """Analyze state changes after command execution"""
        # Calculate state changes
        changes = {
            'height_change': new_state['height'] - prev_state['height'],
            'position_change': np.sqrt(
                (new_state['x_pos'] - prev_state['x_pos'])**2 +
                (new_state['y_pos'] - prev_state['y_pos'])**2
            ),
            'battery_drain': prev_state['battery'] - new_state['battery'],
            'speed_change': new_state['speed'] - prev_state['speed'],
            'timestamp': datetime.now()
        }
        
        # Store state history
        self.state_history = pd.concat([
            self.state_history,
            pd.DataFrame([{**new_state, 'timestamp': datetime.now()}])
        ], ignore_index=True)
        
        # Store command history
        self.command_history = pd.concat([
            self.command_history,
            pd.DataFrame([{**command, 'timestamp': datetime.now()}])
        ], ignore_index=True)
        
        return changes
        
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if len(self.state_history) < 2:
            return {}
            
        latest_states = self.state_history.iloc[-10:]  # Last 10 states
        
        return {
            'avg_battery_drain': latest_states['battery'].diff().mean(),
            'avg_speed': latest_states['speed'].mean(),
            'position_stability': latest_states[['x_pos', 'y_pos']].std().mean(),
            'height_stability': latest_states['height'].std()
        }
        
    def get_command_effectiveness(self) -> Dict:
        """Analyze command effectiveness"""
        if len(self.command_history) < 1:
            return {}
            
        # Group commands by type
        command_groups = self.command_history.groupby('command')
        
        effectiveness = {}
        for cmd, group in command_groups:
            corresponding_states = self.state_history[
                self.state_history['timestamp'].isin(group['timestamp'])
            ]
            
            if len(corresponding_states) > 1:
                effectiveness[cmd] = {
                    'success_rate': group['status'].value_counts().get('success', 0) / len(group),
                    'avg_response_time': np.diff(corresponding_states['timestamp']).mean(),
                    'state_stability': corresponding_states[['x_pos', 'y_pos', 'height']].std().mean()
                }
                
        return effectiveness
        
    def predict_next_state(self, current_state: Dict, command: Dict) -> Dict:
        """Predict next state based on historical data"""
        if len(self.state_history) < 10:
            return current_state
            
        # Simple linear prediction based on recent history
        recent_states = self.state_history.iloc[-5:]
        
        trends = {
            'height': recent_states['height'].diff().mean(),
            'x_pos': recent_states['x_pos'].diff().mean(),
            'y_pos': recent_states['y_pos'].diff().mean(),
            'battery': recent_states['battery'].diff().mean()
        }
        
        predicted_state = current_state.copy()
        for key in trends:
            if key in predicted_state:
                predicted_state[key] += trends[key]
                
        return predicted_state
