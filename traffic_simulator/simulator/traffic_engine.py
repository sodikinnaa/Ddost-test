"""
Traffic Engine Module - Main engine menggunakan asyncio dan aiohttp
"""
import asyncio
import time
import aiohttp
from typing import Optional, Dict, Any, Callable, List
from urllib.parse import urlparse

from .safety import SafetyGuard
from .virtual_user import VirtualUser
from .rate_controller import RateController
from .metrics_collector import MetricsCollector, MetricsSnapshot
from .patterns import steady_pattern, ramp_up_pattern, ramp_down_pattern, combined_pattern
from config import (
    DEFAULT_CONCURRENT_USERS,
    REQUEST_TIMEOUT,
    DEFAULT_THINK_TIME_MIN,
    DEFAULT_THINK_TIME_MAX,
    METRICS_UPDATE_INTERVAL,
)


class TrafficEngine:
    """
    Traffic Engine - Main engine untuk menjalankan traffic simulation
    Menggunakan asyncio dan aiohttp untuk async I/O
    """
    
    def __init__(self, 
                 target_url: str,
                 method: str = "GET",
                 headers: Optional[Dict[str, str]] = None,
                 data: Optional[Any] = None,
                 max_concurrent: int = DEFAULT_CONCURRENT_USERS,
                 target_rps: float = 10.0,
                 duration: Optional[float] = None,
                 ramp_up_time: float = 10.0,
                 ramp_down_time: float = 10.0,
                 traffic_pattern: Optional[Callable[[float], float]] = None,
                 safety_guard: Optional[SafetyGuard] = None):
        """
        Initialize traffic engine
        
        Args:
            target_url: Target URL
            method: HTTP method
            headers: Custom headers
            data: Request data
            max_concurrent: Maximum concurrent users
            target_rps: Target requests per second
            duration: Duration in seconds (None = infinite)
            ramp_up_time: Ramp-up time in seconds
            ramp_down_time: Ramp-down time in seconds
            traffic_pattern: Custom traffic pattern function (optional)
            safety_guard: Safety guard instance (optional)
        """
        self.target_url = target_url
        self.method = method
        self.headers = headers or {}
        self.data = data
        self.max_concurrent = max_concurrent
        self.target_rps = target_rps
        self.duration = duration
        self.ramp_up_time = ramp_up_time
        self.ramp_down_time = ramp_down_time
        self.traffic_pattern = traffic_pattern or steady_pattern(target_rps)
        self.safety_guard = safety_guard or SafetyGuard()
        
        # Initialize components
        self.metrics = MetricsCollector()
        self.rate_controller = RateController(target_rps)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # State
        self.running = False
        self.start_time: Optional[float] = None
        self.virtual_users: List[VirtualUser] = []
        
        # Semaphore untuk limit concurrent connections
        self.connection_semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _create_session(self):
        """Create aiohttp session"""
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.headers
        )
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, url: str, method: str, headers: Dict[str, str],
                           data: Any, user_id: str) -> Dict[str, Any]:
        """
        Make HTTP request menggunakan aiohttp
        
        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            data: Request data
            user_id: User ID for logging
            
        Returns:
            Dictionary dengan request result
        """
        start_time = time.monotonic()
        status_code = 0
        bytes_transferred = 0
        error = False
        error_message = None
        
        async with self.connection_semaphore:
            try:
                # Acquire rate limit permission
                await self.rate_controller.acquire()
                
                if not self.session:
                    await self._create_session()
                
                # Prepare request kwargs
                request_kwargs = {}
                if data:
                    if isinstance(data, dict):
                        request_kwargs['json'] = data
                    else:
                        request_kwargs['data'] = data
                
                # Make request
                async with self.session.request(method, url, headers=headers, **request_kwargs) as response:
                    status_code = response.status
                    
                    # Read response body
                    content = await response.read()
                    bytes_transferred = len(content)
                    
                    # Check if error
                    error = status_code >= 400
                    
            except asyncio.TimeoutError:
                error = True
                error_message = "Timeout"
                bytes_transferred = 0
            except aiohttp.ClientError as e:
                error = True
                error_message = str(e)
                bytes_transferred = 0
            except Exception as e:
                error = True
                error_message = str(e)
                bytes_transferred = 0
            finally:
                latency = time.monotonic() - start_time
                
                # Record metric
                await self.metrics.record_request(
                    status_code=status_code,
                    latency=latency,
                    bytes_transferred=bytes_transferred,
                    error=error,
                    error_message=error_message
                )
                
                return {
                    'status_code': status_code,
                    'latency': latency,
                    'bytes': bytes_transferred,
                    'error': error,
                    'error_message': error_message
                }
    
    async def _virtual_user_task(self, user_id: str):
        """
        Task untuk virtual user
        
        Args:
            user_id: User ID
        """
        user = VirtualUser(
            user_id=user_id,
            target_url=self.target_url,
            method=self.method,
            headers=self.headers,
            data=self.data,
            think_time_min=DEFAULT_THINK_TIME_MIN,
            think_time_max=DEFAULT_THINK_TIME_MAX,
            on_request=self._make_request
        )
        
        self.virtual_users.append(user)
        await user.run_session()
    
    def _update_rate_controller(self, elapsed_time: float):
        """
        Update rate controller berdasarkan traffic pattern
        
        Args:
            elapsed_time: Elapsed time since start
        """
        current_rps = self.traffic_pattern(elapsed_time)
        if hasattr(self.rate_controller, 'adjust_rate'):
            self.rate_controller.adjust_rate(current_rps)
        else:
            # Create new rate controller if not adaptive
            self.rate_controller = RateController(current_rps)
    
    async def _metrics_reporter(self, on_update: Optional[Callable[[MetricsSnapshot], None]] = None):
        """
        Background task untuk report metrics secara berkala
        
        Args:
            on_update: Callback function untuk handle metrics update
        """
        while self.running:
            await asyncio.sleep(METRICS_UPDATE_INTERVAL)
            
            if self.running:
                snapshot = await self.metrics.get_snapshot()
                if on_update:
                    on_update(snapshot)
    
    async def run(self, on_metrics_update: Optional[Callable[[MetricsSnapshot], None]] = None):
        """
        Run traffic simulation
        
        Args:
            on_metrics_update: Callback function untuk handle metrics update
        """
        # Validate target
        is_valid, error_msg = self.safety_guard.validate_all(
            self.target_url,
            target_rps=self.target_rps,
            target_concurrent=self.max_concurrent
        )
        
        if not is_valid:
            raise ValueError(f"Safety check failed: {error_msg}")
        
        self.running = True
        self.start_time = time.monotonic()
        
        try:
            # Create session
            await self._create_session()
            
            # Start metrics reporter
            metrics_task = asyncio.create_task(self._metrics_reporter(on_metrics_update))
            
            # Calculate phases
            main_duration = None
            if self.duration:
                main_duration = self.duration - self.ramp_up_time - self.ramp_down_time
                main_duration = max(0, main_duration)
            
            # Phase 1: Ramp-up
            if self.ramp_up_time > 0:
                ramp_up_pattern_func = ramp_up_pattern(0, self.target_rps, self.ramp_up_time)
                self.traffic_pattern = ramp_up_pattern_func
                
                ramp_up_task = asyncio.create_task(self._run_phase(
                    duration=self.ramp_up_time,
                    update_pattern=True
                ))
                await ramp_up_task
            
            # Phase 2: Main (steady)
            if main_duration is None or main_duration > 0:
                self.traffic_pattern = steady_pattern(self.target_rps)
                main_task = asyncio.create_task(self._run_phase(
                    duration=main_duration,
                    update_pattern=False
                ))
                await main_task
            
            # Phase 3: Ramp-down
            if self.ramp_down_time > 0:
                ramp_down_pattern_func = ramp_down_pattern(self.target_rps, 0, self.ramp_down_time)
                self.traffic_pattern = ramp_down_pattern_func
                
                ramp_down_task = asyncio.create_task(self._run_phase(
                    duration=self.ramp_down_time,
                    update_pattern=True
                ))
                await ramp_down_task
            
            # Stop metrics reporter
            metrics_task.cancel()
            try:
                await metrics_task
            except asyncio.CancelledError:
                pass
        
        finally:
            self.running = False
            
            # Stop all virtual users
            for user in self.virtual_users:
                user.stop()
            
            # Close session
            await self._close_session()
    
    async def _run_phase(self, duration: Optional[float] = None, update_pattern: bool = False):
        """
        Run a phase of simulation
        
        Args:
            duration: Phase duration (None = infinite)
            update_pattern: Whether to update pattern dynamically
        """
        phase_start = time.monotonic()
        user_counter = 0
        tasks = []
        
        # Start initial virtual users
        initial_users = min(self.max_concurrent, max(1, int(self.target_rps)))
        for i in range(initial_users):
            user_id = f"user_{user_counter}"
            user_counter += 1
            task = asyncio.create_task(self._virtual_user_task(user_id))
            tasks.append(task)
        
        # Main loop
        while self.running:
            now = time.monotonic()
            elapsed = now - phase_start
            
            # Check duration
            if duration and elapsed >= duration:
                break
            
            # Update rate controller if needed
            if update_pattern and self.start_time:
                elapsed_total = now - self.start_time
                self._update_rate_controller(elapsed_total)
            
            # Remove completed tasks
            tasks = [t for t in tasks if not t.done()]
            
            # Add new tasks if needed (to maintain concurrency)
            while len(tasks) < self.max_concurrent and self.running:
                user_id = f"user_{user_counter}"
                user_counter += 1
                task = asyncio.create_task(self._virtual_user_task(user_id))
                tasks.append(task)
            
            # Small sleep to prevent busy loop
            await asyncio.sleep(0.1)
        
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop simulation"""
        self.running = False
    
    async def get_final_metrics(self) -> MetricsSnapshot:
        """
        Get final metrics snapshot
        
        Returns:
            Final metrics snapshot
        """
        return await self.metrics.get_snapshot()

