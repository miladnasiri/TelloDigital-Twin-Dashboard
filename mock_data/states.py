import time
import random
from dataclasses import dataclass
from typing import Dict
from config.tello_specs import FLIGHT, VISION

@dataclass
class TelloState:
    height: float = 0.0
    speed: float = 0.0
    battery: int = 100
    temp_low: int = 25
    temp_high: int = 28
    flight_mode: str = "slow"
    vision_system: bool = True
    flight_time: int = 0
    x_pos: float = 0.0
    y_pos: float = 0.0
    yaw_angle: float = 0.0

    def __post_init__(self):
        self.start_time = time.time()
        self.last_update = self.start_time
        self.is_flying = False

    def update(self):
        if self.is_flying:
            current_time = time.time()
            self.flight_time = int(current_time - self.start_time)
            self.temp_low = max(0, min(40, self.temp_low + random.uniform(-0.2, 0.3)))
            self.temp_high = self.temp_low + 3
            self.battery = max(0, self.battery - 0.01)

    def get_state_dict(self) -> Dict:
        self.update()
        return {
            "height": round(self.height, 2),
            "speed": round(self.speed, 2),
            "battery": int(self.battery),
            "flight_time": self.flight_time,
            "temp_low": int(self.temp_low),
            "temp_high": int(self.temp_high),
            "flight_mode": self.flight_mode,
            "vision_system": self.vision_system,
            "x_pos": round(self.x_pos, 2),
            "y_pos": round(self.y_pos, 2),
            "yaw_angle": round(self.yaw_angle, 2)
        }

    def take_off(self) -> bool:
        if not self.is_flying and self.battery > 10:
            self.is_flying = True
            self.height = VISION["HEIGHT_RANGE"]["MIN"]
            self.start_time = time.time()
            return True
        return False

    def land(self) -> bool:
        if self.is_flying:
            self.is_flying = False
            self.height = 0.0
            self.speed = 0.0
            return True
        return False

    def set_height(self, target_height: float) -> bool:
        if not self.is_flying:
            return False
        self.height = max(VISION["HEIGHT_RANGE"]["MIN"],
                         min(VISION["HEIGHT_RANGE"]["MAX"], target_height))
        return True

    def move(self, direction: str, distance: int) -> bool:
        if not self.is_flying:
            return False
            
        distance_m = distance / 100
        
        if direction == "forward":
            self.y_pos += distance_m
        elif direction == "back":
            self.y_pos -= distance_m
        elif direction == "left":
            self.x_pos -= distance_m
        elif direction == "right":
            self.x_pos += distance_m
            
        self.speed = FLIGHT["MAX_SPEED"]["SLOW_MODE"] if self.flight_mode == "slow" else FLIGHT["MAX_SPEED"]["FAST_MODE"]
        return True

    def rotate(self, direction: str, angle: int) -> bool:
        if not self.is_flying:
            return False
            
        if direction == "cw":
            self.yaw_angle = (self.yaw_angle + angle) % 360
        elif direction == "ccw":
            self.yaw_angle = (self.yaw_angle - angle) % 360
        return True
