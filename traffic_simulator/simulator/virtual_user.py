"""
Virtual User Module - Represents a simulated user session
"""
import asyncio
import random
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class UserSession:
    """Represents a user session"""
    user_id: str
    start_time: float
    end_time: Optional[float] = None
    request_count: int = 0
    total_latency: float = 0.0
    total_bytes: int = 0
    errors: int = 0
    

class VirtualUser:
    """
    Virtual User yang mensimulasikan perilaku user nyata:
    - Session-based lifecycle
    - Think time antara requests
    - Realistic request patterns
    """
    
    def __init__(self, 
                 user_id: str,
                 target_url: str,
                 method: str = "GET",
                 headers: Optional[Dict[str, str]] = None,
                 data: Optional[Any] = None,
                 think_time_min: float = 0.5,
                 think_time_max: float = 2.0,
                 session_duration_min: float = 30.0,
                 session_duration_max: float = 300.0,
                 on_request: Optional[Callable] = None):
        """
        Initialize virtual user
        
        Args:
            user_id: Unique identifier untuk user ini
            target_url: URL target untuk requests
            method: HTTP method (GET, POST, etc)
            headers: Custom headers
            data: Request data untuk POST/PUT
            think_time_min: Minimum think time antara requests (seconds)
            think_time_max: Maximum think time antara requests (seconds)
            session_duration_min: Minimum session duration (seconds)
            session_duration_max: Maximum session duration (seconds)
            on_request: Callback function yang dipanggil setiap request
        """
        self.user_id = user_id
        self.target_url = target_url
        self.method = method
        self.headers = headers or {}
        self.data = data
        self.think_time_min = think_time_min
        self.think_time_max = think_time_max
        self.session_duration_min = session_duration_min
        self.session_duration_max = session_duration_max
        self.on_request = on_request
        
        self.session: Optional[UserSession] = None
        self._running = False
    
    async def run_session(self, session: Optional[UserSession] = None):
        """
        Run user session dengan lifecycle:
        1. Start session
        2. Send requests dengan think time
        3. End session setelah duration
        
        Args:
            session: Optional session object (if None, create new)
        """
        if session:
            self.session = session
        else:
            self.session = UserSession(
                user_id=self.user_id,
                start_time=time.monotonic(),
            )
        
        self._running = True
        
        # Determine session duration
        duration = random.uniform(self.session_duration_min, self.session_duration_max)
        end_time = self.session.start_time + duration
        
        try:
            while self._running and time.monotonic() < end_time:
                # Send request
                if self.on_request:
                    result = await self.on_request(
                        self.target_url,
                        self.method,
                        self.headers,
                        self.data,
                        self.user_id
                    )
                    
                    # Update session stats
                    if result:
                        self.session.request_count += 1
                        if 'latency' in result:
                            self.session.total_latency += result['latency']
                        if 'bytes' in result:
                            self.session.total_bytes += result['bytes']
                        if 'error' in result and result['error']:
                            self.session.errors += 1
                
                # Think time (simulate user thinking/browsing)
                think_time = random.uniform(self.think_time_min, self.think_time_max)
                await asyncio.sleep(think_time)
        
        finally:
            self.session.end_time = time.monotonic()
            self._running = False
    
    def stop(self):
        """Stop user session"""
        self._running = False
    
    def get_session_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get session statistics
        
        Returns:
            Dictionary dengan session statistics
        """
        if not self.session:
            return None
        
        duration = (self.session.end_time or time.monotonic()) - self.session.start_time
        avg_latency = self.session.total_latency / self.session.request_count if self.session.request_count > 0 else 0
        
        return {
            'user_id': self.user_id,
            'duration': duration,
            'request_count': self.session.request_count,
            'avg_latency': avg_latency,
            'total_bytes': self.session.total_bytes,
            'errors': self.session.errors,
            'requests_per_second': self.session.request_count / duration if duration > 0 else 0,
        }

