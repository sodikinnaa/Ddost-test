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
    
    # Thread Configuration
    print("\n[*] Thread Configuration:")
    threads_input = input("Jumlah Thread yang akan dijalankan [10]: ").strip()
    num_threads = int(threads_input) if threads_input else 10
    num_threads = max(1, num_threads)  # Minimum 1 thread
    print(f"[*] Menggunakan {num_threads} thread(s)")
    print(f"[*] Note: Semua input akan dikalikan dengan {num_threads} thread")
    
    # Mode & Duration options
    print("\n[*] Execution Mode:")
    print("    - normal: Standard mode dengan delay")
    print("    - spam: High frequency tanpa delay")
    print("    - brutal: MAXIMUM INTENSITY - Use with caution!")
    mode_input = input("Mode (normal/spam/brutal) [normal]: ").strip().lower() or "normal"
    spam_mode = mode_input == "spam"
    brutal_mode = mode_input == "brutal"
    
    if brutal_mode:
        print("\n" + "=" * 60)
        print("⚠️  WARNING: BRUTAL MODE ENABLED")
        print("=" * 60)
        print("This mode is designed to DOWN VPS with 16 Core / 64GB RAM")
        print("\nThis mode will:")
        print("  - Use maximum threads (2000 by default, customizable)")
        print("  - Send requests with ZERO delay")
        print("  - 10 requests per proxy per iteration")
        print("  - 5 iterations per second")
        print("  - Use fire-and-forget method (no waiting)")
        print("  - Generate EXTREME traffic load")
        print("  - Consume maximum CPU, RAM, and bandwidth")
        print("  - Estimated: Up to 200,000+ requests per second (with 10 proxies)")
        print("  - Target: Overwhelm 16 Core CPU and 64GB RAM")
        print("\n⚠️  DANGER: Can cause target system to become unresponsive!")
        print("⚠️  Only use on systems you own or have permission to test!")
        print("\n" + "=" * 60)
        confirm = input("Type 'YES' to continue: ").strip()
        if confirm != "YES":
            print("❌ Brutal mode cancelled.")
            return
        print("=" * 60)
    
    background_input = input("Run in background? (y/n) [n]: ").strip().lower()
    background = background_input == 'y'
    
    # Duration/Waktu kunjungan
    print("\n[*] Waktu Kunjungan (Duration):")
    duration_input = input("Berapa lama kunjungan? (detik, 0 = infinite) [60]: ").strip()
    duration = int(duration_input) if duration_input else 60
    duration = None if duration == 0 else duration
    
    # Spam/Brutal mode options (per thread)
    requests_per_second = None
    total_requests = None
    if spam_mode or brutal_mode:
        print("\n[*] Spam Mode Options (per thread):")
        rps_input = input("Target requests per second per thread (0 = unlimited) [0]: ").strip()
        rps_per_thread = int(rps_input) if rps_input else 0
        if rps_per_thread > 0:
            requests_per_second = rps_per_thread * num_threads  # Kalikan dengan jumlah thread
            print(f"    Total target: {requests_per_second} requests/second ({rps_per_thread} x {num_threads} threads)")
        
        total_input = input("Total requests target per thread (0 = unlimited) [0]: ").strip()
        total_per_thread = int(total_input) if total_input else 0
        if total_per_thread > 0:
            total_requests = total_per_thread * num_threads  # Kalikan dengan jumlah thread
            print(f"    Total target: {total_requests} requests ({total_per_thread} x {num_threads} threads)")

    print("\n[*] Loading proxy from proxy.txt...")
    import os
    # Check if file exists dengan berbagai variasi
    possible_files = ["proxy.txt", " proxy.txt", "proxy.txt ", " proxy.txt "]
    file_exists = False
    actual_file = None
    for fname in possible_files:
        if os.path.exists(fname):
            file_exists = True
            actual_file = fname
            break
    
    if not file_exists:
        # Cari file yang mengandung "proxy" di current directory
        if os.path.exists("."):
            for filename in os.listdir("."):
                if "proxy" in filename.lower() and filename.endswith(".txt"):
                    file_exists = True
                    actual_file = filename
                    break
    
    if file_exists:
        print(f"    [INFO] Found proxy file: {actual_file}")
    else:
        print(f"    [WARNING] proxy.txt not found in current directory")
        print(f"    [INFO] Current directory: {os.getcwd()}")
        print(f"    [INFO] Files in directory: {', '.join([f for f in os.listdir('.') if f.endswith('.txt')][:5])}")
    
    raw_proxies = load_proxies()
    
    if not raw_proxies:
        print("⚠️  No proxies loaded from file. Possible reasons:")
        print("     - File not found or empty")
        print("     - Invalid proxy format (should be: IP:PORT:USERNAME:PASSWORD)")
        print("     - All lines are comments (starting with #)")
        print("   Continuing without proxy validation...")
        valid = []
    else:
        print(f"[✓] Found {len(raw_proxies)} proxies in file")
        print(f"[*] Starting proxy validation...")
        print(f"[*] Test URL: https://ipv4.webshare.io/")
        print("-" * 60)
        
        valid_count = 0
        invalid_count = 0
        valid_proxies_list = []
        
        for i, p in enumerate(raw_proxies, 1):
            # Extract IP untuk display (hide credentials)
            display_proxy = p
            if '@' in p:
                # Format: http://user:pass@ip:port -> show ip:port only
                parts = p.split('@')
                if len(parts) == 2:
                    display_proxy = parts[1]
            
            # Validate dengan verbose untuk mendapatkan error message
            result = validate_proxy(p, verbose=True)
            is_valid, error_msg, returned_ip = result
            
            if is_valid:
                save_valid_proxy(p)
                valid_count += 1
                valid_proxies_list.append(display_proxy)
                status_icon = "✓"
                status_text = f"VALID (returned IP: {returned_ip})"
            else:
                invalid_count += 1
                status_icon = "✗"
                status_text = f"FAILED: {error_msg}"
            
            print(f"    [{i}/{len(raw_proxies)}] {status_icon} {display_proxy}")
            print(f"        → {status_text}")
        
        print("-" * 60)
        print(f"[✓] Validation complete!")
        print(f"    Valid: {valid_count}/{len(raw_proxies)}")
        print(f"    Invalid: {invalid_count}/{len(raw_proxies)}")
        
        if valid_count > 0:
            print(f"\n[+] Valid proxies:")
            for vp in valid_proxies_list:
                print(f"    • {vp}")

        valid = load_valid_proxies()
        print(f"\n[+] Total valid proxies loaded: {len(valid)}")

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
    print(f"  Threads: {num_threads}")
    if brutal_mode:
        print(f"  Mode: BRUTAL ⚠️")
    else:
        print(f"  Mode: {'SPAM' if spam_mode else 'Normal'}")
    print(f"  Background: {background}")
    print(f"  Waktu Kunjungan: {duration if duration else 'Infinite'} detik")
    if spam_mode or brutal_mode:
        if requests_per_second:
            print(f"  Target Rate: {requests_per_second} req/s (total)")
        if total_requests:
            print(f"  Target Total: {total_requests} requests (total)")
    print("=" * 50)

    print("\n[*] Running simulation...")
    
    if background:
        thread, results_container, stop_flag = run_simulation(
            target, valid, 
            method=method, 
            headers=headers, 
            data=data,
            background=True,
            duration=duration,
            spam_mode=spam_mode,
            brutal_mode=brutal_mode,
            requests_per_second=requests_per_second,
            total_requests=total_requests,
            num_threads=num_threads
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
            background=False,
            duration=duration,
            spam_mode=spam_mode,
            brutal_mode=brutal_mode,
            requests_per_second=requests_per_second,
            total_requests=total_requests,
            num_threads=num_threads
        )
    
    # Display summary
    if results:
        print("\n" + "=" * 60)
        print("[✓] Final Result:")
        print("-" * 60)
        summary = summarize(results)
        
        # Calculate additional statistics
        success_rate = (summary['success'] / summary['total_request'] * 100) if summary['total_request'] > 0 else 0
        error_rate = (summary['errors'] / summary['total_request'] * 100) if summary['total_request'] > 0 else 0
        
        print(f"  Total Requests: {summary['total_request']:,}")
        print(f"  ✓ Success: {summary['success']:,} ({success_rate:.1f}%)")
        print(f"  ✗ Errors: {summary['errors']:,} ({error_rate:.1f}%)")
        print(f"  ⏱  Avg Latency: {summary['avg_latency']}s")
        print(f"\n  📦 Total Data Transferred:")
        print(f"     {summary['total_bytes_formatted']}")
        
        # Calculate additional stats
        if summary['total_request'] > 0:
            avg_bytes_per_request = summary['total_bytes'] / summary['total_request']
            from simulator.metrics import format_bytes
            print(f"     • Average per request: {format_bytes(int(avg_bytes_per_request))}")
        
        # Display proxy info
        from simulator.engine import get_proxy_display
        proxy_info = get_proxy_display(valid)
        print(f"  🔗 Proxy: {proxy_info}")
        print("=" * 60)


if __name__ == "__main__":
    main()
