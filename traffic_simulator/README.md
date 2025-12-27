# Internal Traffic Simulator

Professional traffic simulation tool for internal testing only. This tool is designed for **internal/staging environments only** and includes comprehensive safety guards to prevent misuse.

## Features

- **Safe & Controlled**: Only allows internal/staging targets with comprehensive safety guards
- **Realistic Simulation**: Virtual users with session-based lifecycle and think time
- **Precise Rate Control**: Token bucket algorithm for accurate RPS control
- **Valid Metrics**: Real-time collection of RPS, latency (p50/p95/p99), error rate, and throughput
- **Traffic Patterns**: Support for steady, spike, burst, and ramp patterns
- **Async I/O**: Built with asyncio and aiohttp for efficient concurrent requests
- **Professional Reporting**: Detailed summary reports with percentile metrics

## Safety Features

- **Target Validation**: Only allows localhost, private IPs, and allowlisted domains
- **RPS Limits**: Hard limit of 1000 req/s (configurable)
- **Concurrency Limits**: Maximum 500 concurrent connections (configurable)
- **Environment Check**: Validates environment (dev/staging only)
- **IP Blocking**: Blocks all public IPs automatically

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The tool will prompt you for:
- Target URL (must be internal/staging)
- HTTP Method
- Max Concurrent Users
- Target RPS
- Duration
- Ramp-up/Ramp-down time
- Traffic Pattern (steady/spike/burst/ramp)

## Configuration

Edit `config.py` to customize:
- `MAX_RPS_LIMIT`: Maximum RPS hard limit
- `MAX_CONCURRENT_CONNECTIONS`: Maximum concurrent connections
- `ALLOWED_TARGETS`: List of allowed target domains
- Default simulation parameters

## Architecture

- **TrafficEngine**: Main engine using asyncio and aiohttp
- **VirtualUser**: Represents simulated users with session lifecycle
- **RateController**: Precise RPS control using token bucket
- **MetricsCollector**: Collects and calculates valid metrics
- **SafetyGuard**: Comprehensive safety checks and validations
- **Traffic Patterns**: Various traffic pattern generators

## Metrics Collected

- Total Requests
- Successful/Error Requests
- Error Rate (%)
- Average Latency
- Latency Percentiles (p50, p95, p99)
- Requests Per Second (RPS)
- Throughput (MB/s)
- Total Data Transferred

## Traffic Patterns

1. **Steady**: Constant RPS
2. **Spike**: Sudden spike then back to base
3. **Burst**: Periodic bursts
4. **Ramp**: Gradual increase/decrease

## Safety Notice

⚠️ **This tool is for internal testing only!**
- Never use on production systems
- Never target public IPs
- Always use in controlled environments
- Respect rate limits and safety guards

## License

Internal use only - Not for public distribution

