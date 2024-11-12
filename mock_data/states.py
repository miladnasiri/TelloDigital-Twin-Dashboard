# mock_data/states.py
import time
import random
from dataclasses import dataclass
from typing import Dict
import sys
sys.path.append('..')
from config.tello_specs import FLIGHT, VISION

@dataclass
class TelloState:
    # Basic state attributes
    height: float = 0.0
    speed: float = 0.0
    battery: int = 100
    temp_low: int = 25
    temp_high: int = 28
    flight_mode: str = 'slow'
    vision_system: bool = True
    flight_time: int = 0
    x_pos: float = 0.0
    y_pos: float = 0.0
    yaw: float = 0.0
    is_flying: bool = False

    def __post_init__(self):
        self.start_time = time.time()
        self.last_update = self.start_time

    def update(self):
        """Update drone state"""
        if self.is_flying:
            current_time = time.time()
            self.flight_time = int(current_time - self.start_time)
            
            # Update temperature
            self.temp_low = max(0, min(40, self.temp_low + random.uniform(-0.2, 0.3)))
            self.temp_high = self.temp_low + 3
            
            # Small battery drain
            self.battery = max(0, self.battery - 0.01)

    def get_state_dict(self) -> Dict:
        """Get current state"""
        self.update()
        return {
            'height': round(self.height, 2),
            'speed': round(self.speed, 2),
            'battery': int(self.battery),
            'flight_time': self.flight_time,
            'temp_low': int(self.temp_low),
            'temp_high': int(self.temp_high),
            'flight_mode': self.flight_mode,
            'vision_system': self.vision_system,
            'x_pos': round(self.x_pos, 2),
            'y_pos': round(self.y_pos, 2),
            'yaw': round(self.yaw, 2),
            'is_flying': self.is_flying
        }

    def take_off(self) -> bool:
        """Execute takeoff"""
        if not self.is_flying and self.battery > 10:
            self.is_flying = True
            self.height = VISION['HEIGHT_RANGE']['MIN']
            self.start_time = time.time()
            return True
        return False

    def land(self) -> bool:
        """Execute landing"""
        if self.is_flying:
            self.is_flying = False
            self.height = 0.0
            self.speed = 0.0
            return True
        return False

    def set_height(self, target_height: float) -> bool:
        """Set drone height"""
        if not self.is_flying:
            return False
        self.height = max(VISION['HEIGHT_RANGE']['MIN'],
                         min(VISION['HEIGHT_RANGE']['MAX'], target_height))
        return True

    def move(self, direction: str, distance: int) -> bool:
        """Move drone in specified direction"""
        print(f"TelloState move: direction={direction}, distance={distance}")  # Debug log
        
        if not self.is_flying:
            print("Not flying, cannot move")  # Debug log
            return False
            
        distance_m = distance / 100  # Convert cm to meters
        print(f"Moving {distance_m} meters")  # Debug log
        
        if direction == 'forward':
            self.y_pos += distance_m
        elif direction == 'back':
            self.y_pos -= distance_m
        elif direction == 'left':
            self.x_pos -= distance_m
        elif direction == 'right':
            self.x_pos += distance_m
            
        self.speed = FLIGHT['MAX_SPEED']['SLOW_MODE'] if self.flight_mode == 'slow' else FLIGHT['MAX_SPEED']['FAST_MODE']
        print(f"New position: x={self.x_pos}, y={self.y_pos}, speed={self.speed}")  # Debug log
        return True

    def rotate(self, direction: str, angle: int) -> bool:
        """Rotate drone"""
        print(f"TelloState rotate: direction={direction}, angle={angle}")  # Debug log
        
        if not self.is_flying:
            print("Not flying, cannot rotate")  # Debug log
            return False
            
        if direction == 'cw':
            self.yaw = (self.yaw + angle) % 360
        elif direction == 'ccw':
            self.yaw = (self.yaw - angle) % 360
        print(f"New orientation: yaw={self.yaw}")  # Debug log
        return True

    def emergency_stop(self) -> bool:
        """Emergency stop all motors"""
        print("Emergency stop triggered")  # Debug log
        self.is_flying = False
        self.height = 0.0
        self.speed = 0.0
        self.flight_time = 0
        return True

    def set_speed(self, speed: int) -> bool:
        """Set drone speed"""
        print(f"TelloState set_speed: speed={speed}")  # Debug log
        
        if not self.is_flying:
            print("Not flying, cannot set speed")  # Debug log
            return False
        
        if speed < FLIGHT['MAX_SPEED']['SLOW_MODE']:
            self.flight_mode = 'slow'
        else:
            self.flight_mode = 'fast'
            
        self.speed = min(speed, FLIGHT['MAX_SPEED']['FAST_MODE'])
        print(f"Speed set to {self.speed} in {self.flight_mode} mode")  # Debug log
        return True

    def update_position(self, x: float, y: float, z: float) -> bool:
        """Update drone position"""
        print(f"TelloState update_position: x={x}, y={y}, z={z}")  # Debug log
        
        if not self.is_flying:
            print("Not flying, cannot update position")  # Debug log
            return False
            
        self.x_pos = max(-10.0, min(10.0, x))  # Limit to ±10m range
        self.y_pos = max(-10.0, min(10.0, y))
        self.height = max(VISION['HEIGHT_RANGE']['MIN'],
                         min(VISION['HEIGHT_RANGE']['MAX'], z))
        print(f"Position updated to: x={self.x_pos}, y={self.y_pos}, height={self.height}")  # Debug log
        return True

    def get_height(self) -> float:
        """Get current height"""
        return self.height

    def get_speed(self) -> float:
        """Get current speed"""
        return self.speed

    def get_battery(self) -> int:
        """Get battery level"""
        return self.battery

    def get_flight_time(self) -> int:
        """Get flight time"""
        return self.flight_time

    def get_temperature(self) -> tuple:
        """Get temperature range"""
        return (self.temp_low, self.temp_high)

    def is_vision_active(self) -> bool:
        """Check if vision system is active"""
        return self.vision_system

    def get_position(self) -> tuple:
        """Get current position"""
        return (self.x_pos, self.y_pos, self.height)

    def get_orientation(self) -> float:
        """Get current yaw angle"""
        return self.yaw

    def reset_state(self):
        """Reset all state attributes to default"""
        print("Resetting TelloState to default values")  # Debug log
        self.height = 0.0
        self.speed = 0.0
        self.battery = 100
        self.temp_low = 25
        self.temp_high = 28
        self.flight_mode = 'slow'
        self.vision_system = True
        self.flight_time = 0
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.yaw = 0.0
        self.is_flying = False
        self.start_time = time.time()
        self.last_update = self.start_time
