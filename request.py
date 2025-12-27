import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def simple_traffic_simulator(
    url: str,
    total_requests: int = 100,
    concurrency: int = 5,
    delay: float = 0.1,
    timeout: float = 5.0
):
    """
    Simple internal traffic simulator (SAFE)
    
    url             : target (HARUS localhost / internal)
    total_requests  : total request
    concurrency     : jumlah request paralel
    delay           : jeda antar batch (detik)
    timeout         : request timeout
    """

    # Safety guard (WAJIB)
    # if not url.startswith(("http://localhost", "http://127.0.0.1")):
    #     raise ValueError("❌ Target harus localhost / internal")

    def send_request(index):
        try:
            start = time.monotonic()
            r = requests.get(url, timeout=timeout)
            latency = (time.monotonic() - start) * 1000
            return (index, r.status_code, latency)
        except Exception as e:
            return (index, "ERR", str(e))

    results = []
    start_time = time.monotonic()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(total_requests):
            futures.append(executor.submit(send_request, i))

            # batch delay (rate control)
            if i % concurrency == 0:
                time.sleep(delay)

        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.monotonic() - start_time
    rps = len(results) / elapsed if elapsed > 0 else 0

    print("\n=== TRAFFIC SUMMARY ===")
    print(f"Target        : {url}")
    print(f"Total request : {len(results)}")
    print(f"Concurrency   : {concurrency}")
    print(f"Elapsed       : {elapsed:.2f}s")
    print(f"RPS           : {rps:.2f}")

    return results
simple_traffic_simulator(
    url="https://beraffiliate.com/",
    total_requests=10002,
    concurrency=1,
    delay=0.05
)
