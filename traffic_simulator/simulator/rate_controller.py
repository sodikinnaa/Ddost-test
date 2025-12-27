"""
Rate Controller Module - Precise RPS control
"""
import asyncio
import time
from typing import Optional


class RateController:
    """
    Rate controller untuk mengontrol requests per second dengan presisi
    Menggunakan token bucket algorithm
    """
    
    def __init__(self, target_rps: float):
        """
        Initialize rate controller
        
        Args:
            target_rps: Target requests per second
        """
        self.target_rps = target_rps
        self.tokens = 0.0
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
        
        # Minimum interval antara requests (1/target_rps)
        self.min_interval = 1.0 / target_rps if target_rps > 0 else 0
        self.last_request_time = 0.0
    
    async def acquire(self):
        """
        Acquire permission untuk send request
        Block jika rate limit tercapai
        """
        async with self._lock:
            now = time.monotonic()
            
            # Update tokens berdasarkan waktu yang berlalu
            elapsed = now - self.last_update
            self.tokens += elapsed * self.target_rps
            self.tokens = min(self.tokens, self.target_rps)  # Cap at target_rps
            self.last_update = now
            
            # Check jika kita punya token
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                self.last_request_time = now
                return
            
            # Tidak ada token, calculate wait time
            wait_time = (1.0 - self.tokens) / self.target_rps
            
            # Ensure minimum interval
            time_since_last = now - self.last_request_time
            if time_since_last < self.min_interval:
                wait_time = max(wait_time, self.min_interval - time_since_last)
            
            self.last_update = now + wait_time
            await asyncio.sleep(wait_time)
            
            self.tokens = 0.0
            self.last_request_time = time.monotonic()
    
    def get_current_rate(self) -> float:
        """
        Get current rate (estimated)
        
        Returns:
            Current RPS
        """
        return self.target_rps


class AdaptiveRateController(RateController):
    """
    Adaptive rate controller yang bisa adjust rate berdasarkan feedback
    """
    
    def __init__(self, initial_rps: float, min_rps: float = 0.1, max_rps: float = 1000.0):
        """
        Initialize adaptive rate controller
        
        Args:
            initial_rps: Initial target RPS
            min_rps: Minimum RPS
            max_rps: Maximum RPS
        """
        super().__init__(initial_rps)
        self.min_rps = min_rps
        self.max_rps = max_rps
        self.current_rps = initial_rps
    
    def adjust_rate(self, new_rps: float):
        """
        Adjust target rate
        
        Args:
            new_rps: New target RPS
        """
        self.current_rps = max(self.min_rps, min(self.max_rps, new_rps))
        self.target_rps = self.current_rps
        self.min_interval = 1.0 / self.target_rps if self.target_rps > 0 else 0

