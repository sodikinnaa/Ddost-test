"""
Traffic Patterns Module - Different traffic pattern generators
"""
import math
import time
from typing import Callable, Optional


def steady_pattern(target_rps: float) -> Callable[[float], float]:
    """
    Generate steady pattern (constant RPS)
    
    Args:
        target_rps: Constant RPS value
        
    Returns:
        Function that returns target_rps for any time
    """
    def pattern(elapsed_time: float) -> float:
        return target_rps
    
    return pattern


def ramp_up_pattern(start_rps: float, end_rps: float, duration: float) -> Callable[[float], float]:
    """
    Generate ramp-up pattern (gradual increase)
    
    Args:
        start_rps: Starting RPS
        end_rps: Ending RPS
        duration: Duration of ramp-up in seconds
        
    Returns:
        Function that returns RPS based on elapsed time
    """
    def pattern(elapsed_time: float) -> float:
        if elapsed_time >= duration:
            return end_rps
        progress = elapsed_time / duration
        return start_rps + (end_rps - start_rps) * progress
    
    return pattern


def ramp_down_pattern(start_rps: float, end_rps: float, duration: float) -> Callable[[float], float]:
    """
    Generate ramp-down pattern (gradual decrease)
    
    Args:
        start_rps: Starting RPS
        end_rps: Ending RPS
        duration: Duration of ramp-down in seconds
        
    Returns:
        Function that returns RPS based on elapsed time
    """
    def pattern(elapsed_time: float) -> float:
        if elapsed_time >= duration:
            return end_rps
        progress = elapsed_time / duration
        return start_rps - (start_rps - end_rps) * progress
    
    return pattern


def spike_pattern(base_rps: float, spike_rps: float, spike_duration: float,
                  spike_start: float, spike_end: Optional[float] = None) -> Callable[[float], float]:
    """
    Generate spike pattern (sudden increase then back to base)
    
    Args:
        base_rps: Base RPS
        spike_rps: RPS during spike
        spike_duration: Duration of spike in seconds
        spike_start: When spike starts (seconds from start)
        spike_end: When spike ends (seconds from start). If None, calculated from spike_start + spike_duration
        
    Returns:
        Function that returns RPS based on elapsed time
    """
    if spike_end is None:
        spike_end = spike_start + spike_duration
    
    def pattern(elapsed_time: float) -> float:
        if spike_start <= elapsed_time <= spike_end:
            return spike_rps
        return base_rps
    
    return pattern


def burst_pattern(base_rps: float, burst_rps: float, burst_duration: float,
                  burst_interval: float, start_time: float = 0.0) -> Callable[[float], float]:
    """
    Generate burst pattern (periodic bursts)
    
    Args:
        base_rps: Base RPS
        burst_rps: RPS during burst
        burst_duration: Duration of each burst in seconds
        burst_interval: Interval between bursts in seconds
        start_time: When first burst starts (seconds from start)
        
    Returns:
        Function that returns RPS based on elapsed time
    """
    def pattern(elapsed_time: float) -> float:
        if elapsed_time < start_time:
            return base_rps
        
        # Calculate position in burst cycle
        cycle_time = (elapsed_time - start_time) % burst_interval
        
        if cycle_time < burst_duration:
            return burst_rps
        return base_rps
    
    return pattern


def combined_pattern(patterns: list, durations: list) -> Callable[[float], float]:
    """
    Combine multiple patterns sequentially
    
    Args:
        patterns: List of pattern functions
        durations: List of durations for each pattern (in seconds)
        
    Returns:
        Function that returns RPS based on elapsed time
    """
    if len(patterns) != len(durations):
        raise ValueError("patterns and durations must have same length")
    
    cumulative_durations = []
    cumulative = 0.0
    for d in durations:
        cumulative += d
        cumulative_durations.append(cumulative)
    
    def pattern(elapsed_time: float) -> float:
        for i, (pattern_func, cum_duration) in enumerate(zip(patterns, cumulative_durations)):
            if elapsed_time <= cum_duration:
                pattern_start = cumulative_durations[i-1] if i > 0 else 0.0
                pattern_elapsed = elapsed_time - pattern_start
                return pattern_func(pattern_elapsed)
        
        # After all patterns, use last pattern
        pattern_start = cumulative_durations[-2] if len(cumulative_durations) > 1 else 0.0
        pattern_elapsed = elapsed_time - pattern_start
        return patterns[-1](pattern_elapsed)
    
    return pattern

