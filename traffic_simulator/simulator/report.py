"""
Report Module - Generate detailed reports and summaries
"""
from typing import Dict, Any
from .metrics_collector import MetricsSnapshot, RequestMetric


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes ke format yang lebih readable (B, KB, MB, GB)
    
    Args:
        bytes_value: Bytes value
        
    Returns:
        Formatted string
    """
    if bytes_value == 0:
        return "0 B"
    
    bytes_int = int(bytes_value)
    
    kb = bytes_int / 1024
    mb = bytes_int / (1024 * 1024)
    gb = bytes_int / (1024 * 1024 * 1024)
    
    if gb >= 1:
        return f"{gb:.2f} GB ({mb:.2f} MB)"
    elif mb >= 1:
        return f"{mb:.2f} MB ({kb:.2f} KB)"
    elif kb >= 1:
        return f"{kb:.2f} KB"
    else:
        return f"{bytes_int:,} B"


def format_latency(seconds: float) -> str:
    """
    Format latency dalam format yang readable
    
    Args:
        seconds: Latency in seconds
        
    Returns:
        Formatted string
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


def generate_summary_report(snapshot: MetricsSnapshot, total_runtime: float) -> Dict[str, Any]:
    """
    Generate summary report dari metrics snapshot
    
    Args:
        snapshot: Metrics snapshot
        total_runtime: Total runtime in seconds
        
    Returns:
        Dictionary dengan summary report
    """
    return {
        'total_requests': snapshot.total_requests,
        'successful_requests': snapshot.successful_requests,
        'error_requests': snapshot.error_requests,
        'error_rate_percent': snapshot.error_rate,
        'total_bytes': snapshot.total_bytes,
        'total_bytes_formatted': format_bytes(snapshot.total_bytes),
        'avg_latency': snapshot.avg_latency,
        'avg_latency_formatted': format_latency(snapshot.avg_latency),
        'min_latency': snapshot.min_latency,
        'min_latency_formatted': format_latency(snapshot.min_latency),
        'max_latency': snapshot.max_latency,
        'max_latency_formatted': format_latency(snapshot.max_latency),
        'p50_latency': snapshot.p50_latency,
        'p50_latency_formatted': format_latency(snapshot.p50_latency),
        'p95_latency': snapshot.p95_latency,
        'p95_latency_formatted': format_latency(snapshot.p95_latency),
        'p99_latency': snapshot.p99_latency,
        'p99_latency_formatted': format_latency(snapshot.p99_latency),
        'requests_per_second': snapshot.requests_per_second,
        'throughput_mbps': snapshot.throughput_mbps,
        'total_runtime': total_runtime,
        'total_runtime_formatted': f"{total_runtime:.2f} seconds",
    }


def print_summary_report(report: Dict[str, Any]):
    """
    Print summary report ke console
    
    Args:
        report: Report dictionary dari generate_summary_report
    """
    print("\n" + "=" * 70)
    print("TRAFFIC SIMULATION SUMMARY REPORT")
    print("=" * 70)
    
    print(f"\n📊 OVERVIEW:")
    print(f"  Total Runtime:     {report['total_runtime_formatted']}")
    print(f"  Total Requests:    {report['total_requests']:,}")
    print(f"  Successful:        {report['successful_requests']:,} ({100 - report['error_rate_percent']:.2f}%)")
    print(f"  Errors:            {report['error_requests']:,} ({report['error_rate_percent']:.2f}%)")
    
    print(f"\n⚡ PERFORMANCE:")
    print(f"  Requests/Second:   {report['requests_per_second']:.2f} req/s")
    print(f"  Throughput:        {report['throughput_mbps']:.4f} MB/s")
    print(f"  Total Data:        {report['total_bytes_formatted']}")
    
    print(f"\n⏱️  LATENCY:")
    print(f"  Average:           {report['avg_latency_formatted']}")
    print(f"  Minimum:           {report['min_latency_formatted']}")
    print(f"  Maximum:           {report['max_latency_formatted']}")
    print(f"  Median (p50):      {report['p50_latency_formatted']}")
    print(f"  95th percentile:   {report['p95_latency_formatted']}")
    print(f"  99th percentile:   {report['p99_latency_formatted']}")
    
    print("=" * 70 + "\n")


def print_realtime_metrics(snapshot: MetricsSnapshot):
    """
    Print real-time metrics untuk CLI output
    
    Args:
        snapshot: Metrics snapshot
    """
    print(f"[METRICS] RPS: {snapshot.requests_per_second:.1f} | "
          f"Latency: avg={snapshot.avg_latency*1000:.1f}ms p95={snapshot.p95_latency*1000:.1f}ms | "
          f"Errors: {snapshot.error_rate:.1f}% | "
          f"Throughput: {snapshot.throughput_mbps:.2f} MB/s | "
          f"Total: {snapshot.total_requests:,} requests")

