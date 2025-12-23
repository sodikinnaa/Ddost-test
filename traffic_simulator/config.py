MAX_WORKERS = 10
MIN_DELAY = 1.0
REQUEST_TIMEOUT = 5
BACKGROUND_THREADS = True  # Jalankan di background thread

ALLOWED_TARGETS = [
    "http://localhost",
    "https://staging.domainmu.com",
    "https://beraffiliate.com/"
]

PROXY_TEST_URL = "https://beraffiliate.com/"

# Default custom request settings
DEFAULT_METHOD = "GET"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
DEFAULT_DATA = None  # None untuk GET, dict/str untuk POST/PUT
