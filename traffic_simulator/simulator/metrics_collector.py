"""
Metrics Collector Module - Collect and calculate valid metrics
"""
import asyncio
import time
from collections import deque
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class RequestMetric:
    """Single request metric"""
    timestamp: float
    status_code: int
    latency: float
    bytes: int
    error: bool = False
    error_message: Optional[str] = None


@dataclass
class MetricsSnapshot:
    """Metrics snapshot untuk periode tertentu"""
    timestamp: float
    total_requests: int
    successful_requests: int
    error_requests: int
    total_bytes: int
    avg_latency: float
    min_latency: float
    max_latency: float
    p50_latency: float  # median
    p95_latency: float
    p99_latency: float
    requests_per_second: float
    throughput_mbps: float  # megabytes per second
    error_rate: float  # percentage


class MetricsCollector:
    """
    Metrics collector yang mengumpulkan dan menghitung metrics yang valid
    - RPS aktual
    - Latency (avg, p95, p99)
    - Error rate
    - Throughput (bytes/MB per second)
    """
    
    def __init__(self, window_size: float = 60.0):
        """
        Initialize metrics collector
        
        Args:
            window_size: Size of sliding window in seconds
        """
        self.window_size = window_size
        self.metrics: deque = deque()
        self._lock = None  # Will be set by asyncio.Lock() in async context
        self.start_time = time.monotonic()
    
    async def _ensure_lock(self):
        """Ensure lock is initialized"""
        if self._lock is None:
            self._lock = asyncio.Lock()
    
    async def record_request(self, status_code: int, latency: float, 
                            bytes_transferred: int, error: bool = False,
                            error_message: Optional[str] = None):
        """
        Record a single request metric
        
        Args:
            status_code: HTTP status code (or 0 if error)
            latency: Request latency in seconds
            bytes_transferred: Bytes transferred
            error: Whether this was an error
            error_message: Error message if any
        """
        await self._ensure_lock()
        async with self._lock:
            metric = RequestMetric(
                timestamp=time.monotonic(),
                status_code=status_code,
                latency=latency,
                bytes=bytes_transferred,
                error=error,
                error_message=error_message
            )
            self.metrics.append(metric)
            
            # Remove old metrics outside window
            cutoff_time = time.monotonic() - self.window_size
            while self.metrics and self.metrics[0].timestamp < cutoff_time:
                self.metrics.popleft()
    
    async def get_snapshot(self) -> MetricsSnapshot:
        """
        Get current metrics snapshot
        
        Returns:
            MetricsSnapshot dengan semua metrics
        """
        await self._ensure_lock()
        async with self._lock:
            now = time.monotonic()
            
            # Filter metrics within window
            cutoff_time = now - self.window_size
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return MetricsSnapshot(
                    timestamp=now,
                    total_requests=0,
                    successful_requests=0,
                    error_requests=0,
                    total_bytes=0,
                    avg_latency=0.0,
                    min_latency=0.0,
                    max_latency=0.0,
                    p50_latency=0.0,
                    p95_latency=0.0,
                    p99_latency=0.0,
                    requests_per_second=0.0,
                    throughput_mbps=0.0,
                    error_rate=0.0,
                )
            
            # Calculate basic stats
            total_requests = len(recent_metrics)
            successful_requests = len([m for m in recent_metrics if not m.error and 200 <= m.status_code < 400])
            error_requests = len([m for m in recent_metrics if m.error or m.status_code >= 400])
            total_bytes = sum(m.bytes for m in recent_metrics)
            
            # Latency statistics
            latencies = sorted([m.latency for m in recent_metrics])
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                min_latency = latencies[0]
                max_latency = latencies[-1]
                
                # Percentiles
                p50_latency = latencies[len(latencies) // 2]
                p95_index = int(len(latencies) * 0.95)
                p95_latency = latencies[min(p95_index, len(latencies) - 1)]
                p99_index = int(len(latencies) * 0.99)
                p99_latency = latencies[min(p99_index, len(latencies) - 1)]
            else:
                avg_latency = min_latency = max_latency = 0.0
                p50_latency = p95_latency = p99_latency = 0.0
            
            # RPS (based on window)
            time_span = now - cutoff_time if recent_metrics else self.window_size
            requests_per_second = total_requests / time_span if time_span > 0 else 0.0
            
            # Throughput (MB/s)
            throughput_mbps = (total_bytes / (1024 * 1024)) / time_span if time_span > 0 else 0.0
            
            # Error rate (percentage)
            error_rate = (error_requests / total_requests * 100.0) if total_requests > 0 else 0.0
            
            return MetricsSnapshot(
                timestamp=now,
                total_requests=total_requests,
                successful_requests=successful_requests,
                error_requests=error_requests,
                total_bytes=total_bytes,
                avg_latency=avg_latency,
                min_latency=min_latency,
                max_latency=max_latency,
                p50_latency=p50_latency,
                p95_latency=p95_latency,
                p99_latency=p99_latency,
                requests_per_second=requests_per_second,
                throughput_mbps=throughput_mbps,
                error_rate=error_rate,
            )
    
    async def get_all_metrics(self) -> List[RequestMetric]:
        """
        Get all metrics (for final summary)
        
        Returns:
            List of all recorded metrics
        """
        await self._ensure_lock()
        async with self._lock:
            return list(self.metrics)
    
    def get_total_runtime(self) -> float:
        """
        Get total runtime since start
        
        Returns:
            Runtime in seconds
        """
        return time.monotonic() - self.start_time

