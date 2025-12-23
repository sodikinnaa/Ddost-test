def summarize(results):
    if not results:
        return {
            "total_request": 0,
            "success": 0,
            "errors": 0,
            "avg_latency": 0,
            "total_bytes": 0
        }
    
    total = len(results)
    success = len([r for r in results if isinstance(r, (tuple, list)) and len(r) > 0 and r[0] == 200])
    errors = len([r for r in results if isinstance(r, (tuple, list)) and len(r) > 0 and r[0] == "ERR"])
    
    latencies = []
    total_bytes = 0
    
    for r in results:
        if isinstance(r, (tuple, list)) and len(r) > 1:
            if isinstance(r[1], (int, float)) and r[1] > 0:
                latencies.append(r[1])
            if len(r) > 2 and isinstance(r[2], int):
                total_bytes += r[2]
    
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    return {
        "total_request": total,
        "success": success,
        "errors": errors,
        "avg_latency": round(avg_latency, 3),
        "total_bytes": total_bytes
    }
