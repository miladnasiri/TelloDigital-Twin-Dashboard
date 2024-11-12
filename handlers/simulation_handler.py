# handlers/simulation_handler.py

import asyncio
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime
import json

@dataclass
class SimulationRequest:
    command: str
    params: Optional[Dict] = None
    timestamp: datetime = datetime.now()
    request_id: str = ""

@dataclass
class SimulationResponse:
    status: str
    result: Dict
    request_id: str
    timestamp: datetime = datetime.now()

class TelloBridge:
    def __init__(self):
        self.requests_history = []
        self.responses_history = []
        self.current_state = {
            'height': 0.0,
            'battery': 100,
            'x_pos': 0.0,
            'y_pos': 0.0,
            'yaw': 0.0,
            'speed': 0.0,
            'is_flying': False
        }
        
    async def execute_command(self, command: str, params: Optional[Dict] = None) -> Dict:
        """Execute command and return response"""
        print(f"Executing command: {command} with params: {params}")  # Debug log

        # Create request
        request = SimulationRequest(
            command=command,
            params=params,
            request_id=f"{command}_{datetime.now().timestamp()}"
        )
        
        # Log request
        self.requests_history.append({
            'command': request.command,
            'params': request.params,
            'timestamp': request.timestamp.strftime('%H:%M:%S'),
            'request_id': request.request_id
        })
        
        # Simulate processing
        await asyncio.sleep(0.1)
        
        # Process command
        response = await self._process_command(request)
        
        print(f"Command result: {response}")  # Debug log
        print(f"Current state: {self.current_state}")  # Debug log
        
        # Log response
        self.responses_history.append({
            'status': response.status,
            'result': response.result,
            'timestamp': response.timestamp.strftime('%H:%M:%S'),
            'request_id': response.request_id
        })
        
        # Keep only last 10 entries
        if len(self.requests_history) > 10:
            self.requests_history = self.requests_history[-10:]
            self.responses_history = self.responses_history[-10:]
        
        return {
            'status': response.status,
            'result': response.result,
            'request_id': response.request_id
        }
        
    async def _process_command(self, request: SimulationRequest) -> SimulationResponse:
        """Process command and update state"""
        status = 'error'  # Default status
        result = {
            'state_change': {},
            'message': ''
        }
        
        if request.command == 'takeoff':
            if not self.current_state['is_flying']:
                self.current_state['is_flying'] = True
                self.current_state['height'] = 0.3
                result['state_change'] = {'height': 0.3, 'is_flying': True}
                result['message'] = 'Takeoff successful'
                status = 'success'
            else:
                result['message'] = 'Already flying'
                status = 'error'
                
        elif request.command == 'land':
            if self.current_state['is_flying']:
                self.current_state['is_flying'] = False
                self.current_state['height'] = 0.0
                result['state_change'] = {'height': 0.0, 'is_flying': False}
                result['message'] = 'Landing successful'
                status = 'success'
            else:
                result['message'] = 'Already landed'
                status = 'error'
                
        elif request.command == 'move':
            if self.current_state['is_flying']:
                direction = request.params.get('direction', '')
                distance = request.params.get('distance', 0) / 100  # convert to meters
                
                if direction == 'forward':
                    self.current_state['y_pos'] += distance
                elif direction == 'back':
                    self.current_state['y_pos'] -= distance
                elif direction == 'left':
                    self.current_state['x_pos'] -= distance
                elif direction == 'right':
                    self.current_state['x_pos'] += distance
                elif direction == 'up':
                    self.current_state['height'] += distance
                elif direction == 'down':
                    self.current_state['height'] = max(0.3, self.current_state['height'] - distance)
                    
                result['state_change'] = {
                    'x_pos': self.current_state['x_pos'],
                    'y_pos': self.current_state['y_pos'],
                    'height': self.current_state['height']
                }
                result['message'] = f'Moved {direction} {distance}m'
                status = 'success'
            else:
                result['message'] = 'Not flying'
                status = 'error'
                
        elif request.command == 'rotate':
            if self.current_state['is_flying']:
                direction = request.params.get('direction', '')
                angle = request.params.get('angle', 0)
                
                if direction == 'cw':
                    self.current_state['yaw'] = (self.current_state['yaw'] + angle) % 360
                else:
                    self.current_state['yaw'] = (self.current_state['yaw'] - angle) % 360
                    
                result['state_change'] = {'yaw': self.current_state['yaw']}
                result['message'] = f'Rotated {direction} {angle}°'
                status = 'success'
            else:
                result['message'] = 'Not flying'
                status = 'error'
        
        # Update battery based on action
        try:
            # Update battery based on action
            self.current_state['battery'] = max(0, self.current_state['battery'] - 0.1)
        except Exception as e:
            status = 'error'
            result['message'] = f'Command failed: {str(e)}'    

        return SimulationResponse(
            status=status,
            result=result,
            request_id=request.request_id
        )
        
    def get_command_history(self) -> List[Dict]:
        """Get command history with requests and responses"""
        history = []
        for req, res in zip(self.requests_history, self.responses_history):
            history.append({
                'request': req,
                'response': res,
                'time': req['timestamp']
            })
        return history
