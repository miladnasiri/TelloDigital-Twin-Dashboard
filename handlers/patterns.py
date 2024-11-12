
import asyncio
from typing import List, Dict
import math
import numpy as np

class FlightPattern:
    def __init__(self, bridge):
        self.bridge = bridge
        self.min_height = 0.3  # Minimum safe height
        self.max_height = 10.0  # Maximum height
        self.safe_speed = 50   # Safe speed for patterns (cm/s)

    async def square_pattern(self, size: float) -> List[Dict]:
        """Execute square pattern
        Args:
            size: Size of square in centimeters
        """
        # Validate size
        if size < 20 or size > 500:
            return [{'status': 'error', 'message': 'Invalid size. Must be between 20 and 500 cm'}]

        commands = [
            ("move", {"direction": "forward", "distance": size}),
            ("rotate", {"direction": "cw", "angle": 90}),
            ("move", {"direction": "forward", "distance": size}),
            ("rotate", {"direction": "cw", "angle": 90}),
            ("move", {"direction": "forward", "distance": size}),
            ("rotate", {"direction": "cw", "angle": 90}),
            ("move", {"direction": "forward", "distance": size}),
            ("rotate", {"direction": "cw", "angle": 90})
        ]
        
        results = []
        for cmd, params in commands:
            result = await self.bridge.execute_command(cmd, params)
            results.append(result)
            if result['status'] == 'error':
                break
            await asyncio.sleep(0.5)  # Safety delay
        
        return results

    async def spiral_pattern(self, radius: float, height: float) -> List[Dict]:
        """Execute spiral pattern
        Args:
            radius: Spiral radius in centimeters
            height: Total height to climb in centimeters
        """
        # Validate parameters
        if radius < 30 or radius > 150:
            return [{'status': 'error', 'message': 'Invalid radius. Must be between 30 and 150 cm'}]
        if height < 50 or height > 200:
            return [{'status': 'error', 'message': 'Invalid height. Must be between 50 and 200 cm'}]

        steps = 8  # Number of segments in spiral
        angle_step = 360 / steps
        height_step = height / steps
        radius_step = radius / steps
        
        results = []
        
        # Initial positioning
        start_height = await self.bridge.execute_command("move", {"direction": "up", "distance": 50})
        results.append(start_height)
        if start_height['status'] == 'error':
            return results

        for i in range(steps):
            # Calculate current radius for this step
            current_radius = radius_step * (i + 1)
            
            # Move up
            up_cmd = await self.bridge.execute_command(
                "move",
                {"direction": "up", "distance": height_step}
            )
            results.append(up_cmd)
            if up_cmd['status'] == 'error':
                break

            # Rotate
            rotate_cmd = await self.bridge.execute_command(
                "rotate",
                {"direction": "cw", "angle": angle_step}
            )
            results.append(rotate_cmd)
            if rotate_cmd['status'] == 'error':
                break

            # Move outward
            forward_cmd = await self.bridge.execute_command(
                "move",
                {"direction": "forward", "distance": current_radius}
            )
            results.append(forward_cmd)
            if forward_cmd['status'] == 'error':
                break

            await asyncio.sleep(0.5)  # Safety delay

        return results

    async def circle_pattern(self, radius: float, height: float = None) -> List[Dict]:
        """Execute circular pattern
        Args:
            radius: Circle radius in centimeters
            height: Optional height to maintain
        """
        if radius < 30 or radius > 150:
            return [{'status': 'error', 'message': 'Invalid radius. Must be between 30 and 150 cm'}]

        steps = 16  # Number of segments to approximate circle
        angle_step = 360 / steps
        segment_length = 2 * math.pi * radius / steps
        
        results = []
        
        # Set height if specified
        if height is not None:
            height_cmd = await self.bridge.execute_command(
                "move",
                {"direction": "up", "distance": height}
            )
            results.append(height_cmd)
            if height_cmd['status'] == 'error':
                return results

        for _ in range(steps):
            # Move forward
            forward_cmd = await self.bridge.execute_command(
                "move",
                {"direction": "forward", "distance": segment_length}
            )
            results.append(forward_cmd)
            if forward_cmd['status'] == 'error':
                break

            # Rotate
            rotate_cmd = await self.bridge.execute_command(
                "rotate",
                {"direction": "cw", "angle": angle_step}
            )
            results.append(rotate_cmd)
            if rotate_cmd['status'] == 'error':
                break

            await asyncio.sleep(0.5)

        return results

    async def figure_eight(self, size: float) -> List[Dict]:
        """Execute figure-eight pattern
        Args:
            size: Size of pattern in centimeters
        """
        if size < 50 or size > 300:
            return [{'status': 'error', 'message': 'Invalid size. Must be between 50 and 300 cm'}]

        steps = 16  # Steps per circle
        angle_step = 360 / steps
        radius = size / 2
        
        results = []
        
        # First circle (clockwise)
        for _ in range(steps):
            forward_cmd = await self.bridge.execute_command(
                "move",
                {"direction": "forward", "distance": radius}
            )
            results.append(forward_cmd)
            if forward_cmd['status'] == 'error':
                break

            rotate_cmd = await self.bridge.execute_command(
                "rotate",
                {"direction": "cw", "angle": angle_step}
            )
            results.append(rotate_cmd)
            if rotate_cmd['status'] == 'error':
                break

            await asyncio.sleep(0.5)

        # Transition to second circle
        transition = await self.bridge.execute_command(
            "move",
            {"direction": "forward", "distance": size}
        )
        results.append(transition)
        if transition['status'] == 'error':
            return results

        # Second circle (counter-clockwise)
        for _ in range(steps):
            forward_cmd = await self.bridge.execute_command(
                "move",
                {"direction": "forward", "distance": radius}
            )
            results.append(forward_cmd)
            if forward_cmd['status'] == 'error':
                break

            rotate_cmd = await self.bridge.execute_command(
                "rotate",
                {"direction": "ccw", "angle": angle_step}
            )
            results.append(rotate_cmd)
            if rotate_cmd['status'] == 'error':
                break

            await asyncio.sleep(0.5)

        return results

    def _validate_battery(self, min_required: int = 20) -> bool:
        """Check if battery level is sufficient for pattern execution"""
        state = self.bridge.get_state()
        return state.get('battery', 0) >= min_required

    def _estimate_pattern_duration(self, commands: List) -> float:
        """Estimate time needed to execute pattern"""
        total_time = 0
        for cmd, params in commands:
            if cmd == "move":
                distance = params.get("distance", 0)
                total_time += distance / self.safe_speed
            elif cmd == "rotate":
                angle = params.get("angle", 0)
                total_time += angle / 90  # Assume 1 second per 90 degrees
        return total_time

