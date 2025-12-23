import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import MAX_WORKERS, MIN_DELAY
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

def run_simulation(target, proxies, method=None, headers=None, data=None, background=False, duration=None):
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
    """
    results = SimulationResults() if background else []
    
    def _run_single_iteration():
        """Jalankan satu iterasi request ke semua proxy"""
        iteration_results = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = []
            for proxy in proxies:
                future = pool.submit(run_request, target, proxy, method, headers, data)
                futures.append(future)
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    iteration_results.append(result)
                except Exception as e:
                    iteration_results.append(("ERR", 0, str(e)))
            
            time.sleep(MIN_DELAY)
        
        return iteration_results
    
    if background:
        # Jalankan di background thread
        stop_flag = threading.Event()
        
        def background_worker():
            start_time = time.time()
            iteration = 0
            
            while not stop_flag.is_set():
                if duration and (time.time() - start_time) >= duration:
                    break
                
                iteration += 1
                iteration_results = _run_single_iteration()
                results.extend(iteration_results)
                
                if iteration % 10 == 0:
                    count = results.count()
                    elapsed = time.time() - start_time
                    print(f"[*] Background: {count} requests sent (elapsed: {elapsed:.1f}s)")
            
            count = results.count()
            print(f"\n[✓] Background simulation completed. Total requests: {count}")
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        print("[*] Simulation running in background thread...")
        print(f"[*] Use Ctrl+C to stop (duration: {duration}s)" if duration else "[*] Use Ctrl+C to stop")
        
        # Return thread object dan results container
        return thread, results, stop_flag
    else:
        # Jalankan normal (blocking)
        if duration:
            # Jalankan berulang selama duration
            start_time = time.time()
            iteration = 0
            while (time.time() - start_time) < duration:
                iteration += 1
                iteration_results = _run_single_iteration()
                results.extend(iteration_results)
                print(f"[*] Iteration {iteration}: {len(results)} total requests")
        else:
            # Jalankan sekali
            results = _run_single_iteration()
        
        return None, results, None
