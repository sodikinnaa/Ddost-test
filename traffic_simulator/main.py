import json
import time
from utils.proxy import load_proxies, save_valid_proxy, load_valid_proxies
from utils.validator import validate_proxy, validate_target
from simulator.engine import run_simulation
from simulator.metrics import summarize

def parse_headers(headers_str):
    """Parse headers dari string format key:value,key2:value2"""
    if not headers_str:
        return None
    headers = {}
    for pair in headers_str.split(","):
        if ":" in pair:
            key, value = pair.split(":", 1)
            headers[key.strip()] = value.strip()
    return headers

def parse_data(data_str):
    """Parse data dari JSON string atau plain string"""
    if not data_str:
        return None
    try:
        # Coba parse sebagai JSON
        return json.loads(data_str)
    except json.JSONDecodeError:
        # Jika bukan JSON, return sebagai string
        return data_str

def main():
    print("=" * 50)
    print("Traffic Simulator - Custom Request & Background Thread")
    print("=" * 50)
    
    target = input("\nTarget URL: ").strip()

    if not validate_target(target):
        print("❌ Target tidak diizinkan")
        return

    # Custom request options
    print("\n[*] Custom Request Options (press Enter for default):")
    method = input("HTTP Method (GET/POST/PUT/DELETE) [GET]: ").strip().upper() or "GET"
    
    headers_input = input("Custom Headers (format: key:value,key2:value2) [skip]: ").strip()
    headers = parse_headers(headers_input)
    
    data_input = input("Request Data/Body (JSON string or plain text) [skip]: ").strip()
    data = parse_data(data_input)
    
    # Background & duration options
    background_input = input("Run in background? (y/n) [n]: ").strip().lower()
    background = background_input == 'y'
    
    duration = None
    if background:
        duration_input = input("Duration in seconds (0 = infinite) [0]: ").strip()
        duration = int(duration_input) if duration_input else 0
        duration = None if duration == 0 else duration

    print("\n[*] Load proxy...")
    proxies = load_proxies()
    
    if not proxies:
        print("⚠️  No proxies found in proxy.txt. Please add proxies to proxy.txt file.")
        print("   Continuing without proxy validation...")
        valid = []
    else:
        print(f"[*] Found {len(proxies)} proxies")
        print("[*] Validating proxy...")
        for p in proxies:
            if validate_proxy(p):
                save_valid_proxy(p)

        valid = load_valid_proxies()
        print(f"[+] Proxy valid: {len(valid)}")

    if not valid:
        print("⚠️  No valid proxies found. Running simulation without proxy...")
        # Jalankan 1 request tanpa proxy sebagai fallback
        valid = [None]

    # Summary request config
    print("\n" + "=" * 50)
    print("Request Configuration:")
    print(f"  Target: {target}")
    print(f"  Method: {method}")
    print(f"  Headers: {headers if headers else 'Default'}")
    print(f"  Data: {data if data else 'None'}")
    print(f"  Proxies: {len(valid)}")
    print(f"  Background: {background}")
    if duration:
        print(f"  Duration: {duration}s")
    print("=" * 50)

    print("\n[*] Running simulation...")
    
    if background:
        thread, results_container, stop_flag = run_simulation(
            target, valid, 
            method=method, 
            headers=headers, 
            data=data,
            background=True,
            duration=duration
        )
        
        try:
            # Wait for thread to complete atau interrupt
            if thread:
                thread.join()
        except KeyboardInterrupt:
            print("\n[!] Stopping simulation...")
            if stop_flag:
                stop_flag.set()
            if thread:
                thread.join(timeout=2)
            print("[!] Simulation stopped by user")
        
        # Get final results
        results = results_container.get_all() if hasattr(results_container, 'get_all') else results_container
    else:
        _, results, _ = run_simulation(
            target, valid,
            method=method,
            headers=headers,
            data=data,
            background=False
        )
    
    # Display summary
    if results:
        print("\n[✓] Final Result:")
        summary = summarize(results)
        print(f"  Total Requests: {summary['total_request']}")
        print(f"  Success: {summary['success']}")
        print(f"  Errors: {summary['errors']}")
        print(f"  Avg Latency: {summary['avg_latency']}s")
        print(f"  Total Bytes: {summary['total_bytes']}")


if __name__ == "__main__":
    main()
