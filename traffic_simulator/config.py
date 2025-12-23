MAX_WORKERS = 10
MIN_DELAY = 1.0
REQUEST_TIMEOUT = 5
BACKGROUND_THREADS = True  # Jalankan di background thread

# Spam mode settings
SPAM_MODE_DELAY = 0.0  # No delay untuk spam mode
SPAM_MAX_WORKERS = 50  # Lebih banyak workers untuk spam

# Brutal mode settings (EXTREME INTENSITY - TARGET: 1 MILLION REQUESTS/SECOND!)
BRUTAL_MODE_DELAY = 0.0  # Absolutely no delay
BRUTAL_MAX_WORKERS = 5000  # Maximum workers untuk brutal mode (target: 1M req/s)
BRUTAL_REQUEST_TIMEOUT = 0.1  # Ultra short timeout untuk maximum throughput
BRUTAL_KEEP_ALIVE = True  # Keep connection alive untuk reuse (faster)
BRUTAL_FIRE_AND_FORGET = True  # Don't wait for full response
BRUTAL_REQUESTS_PER_ITERATION = 50  # Multiple requests per thread per iteration (target: 1M req/s)
BRUTAL_CONCURRENT_CONNECTIONS = 50  # Multiple concurrent connections per worker
BRUTAL_ITERATIONS_PER_SECOND = 10  # Multiple iterations per second untuk maximum load
BRUTAL_BATCH_SIZE = 1000  # Batch size untuk parallel processing

ALLOWED_TARGETS = [
    "http://localhost",
    "https://staging.domainmu.com",
    "https://beraffiliate.com/",
    "https://adilsempoamandiri.com/",
    "http://127.0.0.1:8001/"
]

PROXY_TEST_URL = "https://beraffiliate.com/"

# Default custom request settings
DEFAULT_METHOD = "GET"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
DEFAULT_DATA = None  # None untuk GET, dict/str untuk POST/PUT
