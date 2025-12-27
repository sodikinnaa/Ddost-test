"""
Internal Traffic Simulator - Main Entry Point
Professional traffic simulation tool for internal testing only
"""
import asyncio
import sys
from simulator.safety import SafetyGuard
from simulator.traffic_engine import TrafficEngine
from simulator.report import print_summary_report, print_realtime_metrics, generate_summary_report
from simulator.patterns import steady_pattern, spike_pattern, burst_pattern, ramp_up_pattern
from config import (
    DEFAULT_CONCURRENT_USERS,
    DEFAULT_DURATION,
    DEFAULT_TARGET_RPS,
    DEFAULT_RAMP_UP_TIME,
    DEFAULT_RAMP_DOWN_TIME,
    DEFAULT_METHOD,
    DEFAULT_HEADERS,
    TRAFFIC_PATTERN_STEADY,
    TRAFFIC_PATTERN_SPIKE,
    TRAFFIC_PATTERN_BURST,
    TRAFFIC_PATTERN_RAMP,
    MAX_RPS_LIMIT,
    MAX_CONCURRENT_CONNECTIONS,
)


def get_user_input(prompt: str, default: str = "", input_type: type = str):
    """
    Get user input dengan default value
    
    Args:
        prompt: Input prompt
        default: Default value
        input_type: Type untuk conversion
        
    Returns:
        User input converted to type
    """
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    value = input(full_prompt).strip()
    if not value:
        return input_type(default) if default else None
    
    try:
        return input_type(value)
    except ValueError:
        print(f"⚠️  Invalid input, using default: {default}")
        return input_type(default) if default else None


def select_traffic_pattern(target_rps: float) -> callable:
    """
    Select traffic pattern berdasarkan user input
    
    Args:
        target_rps: Target RPS
        
    Returns:
        Pattern function
    """
    print("\n[*] Traffic Pattern:")
    print("    1. Steady - Constant RPS")
    print("    2. Spike - Sudden spike then back to base")
    print("    3. Burst - Periodic bursts")
    print("    4. Ramp - Gradual increase")
    
    choice = get_user_input("Select pattern (1-4)", "1", int)
    
    if choice == 1:
        return steady_pattern(target_rps)
    elif choice == 2:
        base_rps = target_rps * 0.5
        spike_rps = target_rps * 2.0
        spike_start = get_user_input("Spike start time (seconds)", "10", float)
        spike_duration = get_user_input("Spike duration (seconds)", "5", float)
        return spike_pattern(base_rps, spike_rps, spike_duration, spike_start)
    elif choice == 3:
        base_rps = target_rps * 0.3
        burst_rps = target_rps * 2.0
        burst_duration = get_user_input("Burst duration (seconds)", "2", float)
        burst_interval = get_user_input("Burst interval (seconds)", "10", float)
        return burst_pattern(base_rps, burst_rps, burst_duration, burst_interval)
    elif choice == 4:
        start_rps = get_user_input("Start RPS", str(target_rps * 0.2), float)
        ramp_duration = get_user_input("Ramp duration (seconds)", "30", float)
        return ramp_up_pattern(start_rps, target_rps, ramp_duration)
    else:
        return steady_pattern(target_rps)


async def run_simulation_async(engine: TrafficEngine):
    """
    Run simulation dengan real-time metrics reporting
    
    Args:
        engine: TrafficEngine instance
    """
    def on_metrics_update(snapshot):
        """Callback untuk update metrics"""
        print_realtime_metrics(snapshot)
    
    try:
        await engine.run(on_metrics_update=on_metrics_update)
    except KeyboardInterrupt:
        print("\n[!] Simulation interrupted by user")
        await engine.stop()
    except Exception as e:
        print(f"\n[✗] Error during simulation: {e}")
        raise


def main():
    """Main function"""
    print("=" * 70)
    print("INTERNAL TRAFFIC SIMULATOR")
    print("Professional Traffic Simulation Tool for Internal Testing")
    print("=" * 70)
    
    # Initialize safety guard
    safety_guard = SafetyGuard()
    
    # Check environment
    env_ok, env_msg = safety_guard.check_environment()
    if not env_ok:
        print(f"⚠️  {env_msg}")
        print("⚠️  This tool is intended for internal testing only.")
        proceed = input("Continue anyway? (yes/no): ").strip().lower()
        if proceed != 'yes':
            print("❌ Aborted.")
            return
    
    # Get target URL
    print("\n[*] Target Configuration:")
    target_url = get_user_input("Target URL", "")
    
    if not target_url:
        print("❌ Target URL is required")
        return
    
    # Validate target
    is_valid, error_msg = safety_guard.validate_target(target_url)
    if not is_valid:
        print(f"❌ {error_msg}")
        print("⚠️  Only internal/staging targets are allowed for safety.")
        return
    
    # Request configuration
    print("\n[*] Request Configuration:")
    method = get_user_input("HTTP Method (GET/POST/PUT/DELETE)", DEFAULT_METHOD, str).upper()
    
    # Simulation configuration
    print("\n[*] Simulation Configuration:")
    max_concurrent = get_user_input(
        f"Max Concurrent Users (max {MAX_CONCURRENT_CONNECTIONS})",
        str(DEFAULT_CONCURRENT_USERS),
        int
    )
    max_concurrent = min(max_concurrent, MAX_CONCURRENT_CONNECTIONS)
    
    target_rps = get_user_input(
        f"Target RPS (max {MAX_RPS_LIMIT})",
        str(DEFAULT_TARGET_RPS),
        float
    )
    target_rps = min(target_rps, MAX_RPS_LIMIT)
    
    # Validate RPS and concurrency
    rps_ok, rps_msg = safety_guard.validate_rps(target_rps)
    if not rps_ok:
        print(f"⚠️  {rps_msg}")
        target_rps = MAX_RPS_LIMIT
        print(f"⚠️  Using maximum allowed: {target_rps} req/s")
    
    concurrent_ok, concurrent_msg = safety_guard.validate_concurrency(max_concurrent)
    if not concurrent_ok:
        print(f"⚠️  {concurrent_msg}")
        max_concurrent = MAX_CONCURRENT_CONNECTIONS
        print(f"⚠️  Using maximum allowed: {max_concurrent}")
    
    duration = get_user_input("Duration (seconds, 0 = infinite)", str(DEFAULT_DURATION), float)
    duration = None if duration == 0 else duration
    
    ramp_up_time = get_user_input("Ramp-up time (seconds)", str(DEFAULT_RAMP_UP_TIME), float)
    ramp_down_time = get_user_input("Ramp-down time (seconds)", str(DEFAULT_RAMP_DOWN_TIME), float)
    
    # Traffic pattern
    traffic_pattern = select_traffic_pattern(target_rps)
    
    # Summary
    print("\n" + "=" * 70)
    print("SIMULATION CONFIGURATION:")
    print(f"  Target URL:        {target_url}")
    print(f"  HTTP Method:       {method}")
    print(f"  Max Concurrent:    {max_concurrent} users")
    print(f"  Target RPS:        {target_rps:.1f} req/s")
    print(f"  Duration:          {duration if duration else 'Infinite'} seconds")
    print(f"  Ramp-up:           {ramp_up_time} seconds")
    print(f"  Ramp-down:         {ramp_down_time} seconds")
    print("=" * 70)
    
    confirm = input("\n[*] Start simulation? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Aborted.")
        return
    
    # Create traffic engine
    engine = TrafficEngine(
        target_url=target_url,
        method=method,
        headers=DEFAULT_HEADERS.copy(),
        max_concurrent=max_concurrent,
        target_rps=target_rps,
        duration=duration,
        ramp_up_time=ramp_up_time,
        ramp_down_time=ramp_down_time,
        traffic_pattern=traffic_pattern,
        safety_guard=safety_guard
    )
    
    # Run simulation
    print("\n[*] Starting simulation...")
    print("[*] Press Ctrl+C to stop\n")
    
    async def run_complete_simulation():
        """Run complete simulation and generate report"""
        try:
            await run_simulation_async(engine)
        except KeyboardInterrupt:
            print("\n[!] Simulation stopped by user")
            await engine.stop()
        finally:
            # Get final metrics
            final_snapshot = await engine.get_final_metrics()
            total_runtime = engine.metrics.get_total_runtime()
            
            # Generate and print report
            report = generate_summary_report(final_snapshot, total_runtime)
            print_summary_report(report)
    
    try:
        asyncio.run(run_complete_simulation())
    except Exception as e:
        print(f"\n[✗] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
