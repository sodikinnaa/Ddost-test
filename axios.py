import asyncio
import aiohttp
import time
from typing import Optional

url = "https://beraffiliate.com/"

# Configuration
MAX_CONCURRENT = 500  # Maximum concurrent connections
TOTAL_REQUESTS = 2000  # Total requests to send
TIMEOUT_SECONDS = 30  # Request timeout in seconds
REQUEST_DELAY = 0.01  # Small delay between requests (optional)

# Statistics
success_count = 0
error_count = 0
timeout_count = 0
start_time = None

async def tugas(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, request_id: int):
    """
    Execute single HTTP request dengan error handling
    
    Args:
        session: aiohttp session
        semaphore: Semaphore untuk limit concurrent requests
        request_id: Request ID untuk logging
    """
    global success_count, error_count, timeout_count
    
    async with semaphore:  # Limit concurrent requests
        try:
            async with session.get(url) as response:
                # Read response (optional - bisa di-skip untuk speed)
                # await response.text()
                status = response.status
                
                if 200 <= status < 400:
                    success_count += 1
                else:
                    error_count += 1
                    
        except asyncio.TimeoutError:
            timeout_count += 1
        except aiohttp.ClientError as e:
            error_count += 1
        except Exception as e:
            error_count += 1
        finally:
            # Small delay untuk prevent overwhelming
            if REQUEST_DELAY > 0:
                await asyncio.sleep(REQUEST_DELAY)

async def main():
    """
    Main function dengan proper error handling dan rate limiting
    """
    global start_time
    
    print(f"[*] Starting requests to: {url}")
    print(f"[*] Total requests: {TOTAL_REQUESTS}")
    print(f"[*] Max concurrent: {MAX_CONCURRENT}")
    print(f"[*] Timeout: {TIMEOUT_SECONDS}s")
    print(f"[*] Request delay: {REQUEST_DELAY}s")
    print()
    
    start_time = time.time()
    
    # Create connector dengan limit
    conn = aiohttp.TCPConnector(
        limit=MAX_CONCURRENT,  # Total connection pool size
        limit_per_host=MAX_CONCURRENT,  # Per-host limit
        ttl_dns_cache=300,  # DNS cache TTL
        force_close=False,  # Keep connections alive
    )
    
    # Create timeout
    timeout = aiohttp.ClientTimeout(
        total=TIMEOUT_SECONDS,  # Total timeout
        connect=10,  # Connection timeout
        sock_read=20  # Socket read timeout
    )
    
    # Create semaphore untuk rate limiting
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async with aiohttp.ClientSession(
        connector=conn,
        timeout=timeout,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    ) as session:
        # Create tasks
        tasks = []
        for i in range(TOTAL_REQUESTS):
            task = tugas(session, semaphore, i + 1)
            tasks.append(task)
        
        # Execute dengan error handling
        try:
            # Use gather dengan return_exceptions untuk handle errors gracefully
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count exceptions
            exceptions = [r for r in results if isinstance(r, Exception)]
            if exceptions:
                error_count += len(exceptions)
                
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
        except Exception as e:
            print(f"\n[✗] Error: {e}")
    
    # Print statistics
    elapsed = time.time() - start_time
    total_processed = success_count + error_count + timeout_count
    rps = total_processed / elapsed if elapsed > 0 else 0
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"  Total Requests:    {TOTAL_REQUESTS}")
    print(f"  Processed:          {total_processed}")
    print(f"  ✓ Success:         {success_count} ({success_count/total_processed*100:.1f}%)" if total_processed > 0 else "  ✓ Success:         0")
    print(f"  ✗ Errors:          {error_count} ({error_count/total_processed*100:.1f}%)" if total_processed > 0 else "  ✗ Errors:          0")
    print(f"  ⏱  Timeouts:        {timeout_count} ({timeout_count/total_processed*100:.1f}%)" if total_processed > 0 else "  ⏱  Timeouts:        0")
    print(f"  ⏱  Elapsed Time:    {elapsed:.2f} seconds")
    print(f"  📊 Requests/sec:    {rps:.2f} req/s")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
    except Exception as e:
        print(f"\n[✗] Fatal error: {e}")
        import traceback
        traceback.print_exc()
