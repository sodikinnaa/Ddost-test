"""
Configuration for Internal Traffic Simulator
Safety-first configuration for internal testing only
"""
from typing import List

# ============================================================================
# SAFETY CONFIGURATION
# ============================================================================

# Maximum RPS hard limit (safety guard)
# ⚠️ Untuk load testing ekstrem, bisa dinaikkan (lihat MAXIMUM_LOAD_CONFIG.md)
MAX_RPS_LIMIT = 1000  # requests per second (default: 1000, max recommended: 5000+)

# Maximum concurrent connections
# ⚠️ Untuk load testing ekstrem, bisa dinaikkan (lihat MAXIMUM_LOAD_CONFIG.md)
MAX_CONCURRENT_CONNECTIONS = 500  # default: 500, max recommended: 2000+

# Allowed environments (only allow internal testing environments)
ALLOWED_ENVIRONMENTS = ['development', 'staging', 'test', 'local']

# Allowed target domains (internal and staging only)
ALLOWED_TARGETS = [
    "http://localhost",
    "https://localhost",
    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "https://staging.domainmu.com",
    "https://beraffiliate.com",
    "https://adilsempoamandiri.com",
]

# ============================================================================
# SIMULATION CONFIGURATION
# ============================================================================

# Default simulation settings
DEFAULT_CONCURRENT_USERS = 10  # Virtual users (concurrent connections)
DEFAULT_DURATION = 60  # seconds
DEFAULT_TARGET_RPS = 10  # requests per second (steady state)
DEFAULT_RAMP_UP_TIME = 10  # seconds to reach target RPS
DEFAULT_RAMP_DOWN_TIME = 10  # seconds to ramp down

# Request settings
REQUEST_TIMEOUT = 30  # seconds (realistic timeout for internal testing)
CONNECTION_TIMEOUT = 10  # seconds
MAX_RETRIES = 2  # retry failed requests

# Virtual user settings
DEFAULT_THINK_TIME_MIN = 0.5  # seconds (min think time between requests)
DEFAULT_THINK_TIME_MAX = 2.0  # seconds (max think time between requests)
DEFAULT_SESSION_DURATION_MIN = 30  # seconds (min session duration)
DEFAULT_SESSION_DURATION_MAX = 300  # seconds (max session duration)

# Metrics collection
METRICS_WINDOW_SIZE = 60  # seconds (sliding window for metrics)
METRICS_UPDATE_INTERVAL = 1.0  # seconds (update metrics every N seconds)

# ============================================================================
# HTTP REQUEST SETTINGS
# ============================================================================

DEFAULT_METHOD = "GET"
DEFAULT_HEADERS = {
    "User-Agent": "Internal-Traffic-Simulator/1.0",
    "Accept": "text/html,application/json,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

DEFAULT_DATA = None  # None untuk GET, dict/str untuk POST/PUT

# ============================================================================
# TRAFFIC PATTERNS
# ============================================================================

# Traffic pattern types
TRAFFIC_PATTERN_STEADY = "steady"  # Constant RPS
TRAFFIC_PATTERN_SPIKE = "spike"    # Sudden spike then back
TRAFFIC_PATTERN_BURST = "burst"    # Periodic bursts
TRAFFIC_PATTERN_RAMP = "ramp"      # Gradual increase/decrease
