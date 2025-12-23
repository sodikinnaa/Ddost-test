def format_bytes(bytes_value):
    """
    Format bytes ke format yang lebih readable (B, KB, MB, GB, TB)
    Returns formatted string dengan breakdown detail
    """
    if bytes_value == 0:
        return "0 B"
    
    bytes_int = int(bytes_value)
    
    # Calculate all units untuk breakdown
    kb = bytes_int / 1024
    mb = bytes_int / (1024 * 1024)
    gb = bytes_int / (1024 * 1024 * 1024)
    tb = bytes_int / (1024 * 1024 * 1024 * 1024)
    
    # Pilih unit yang paling sesuai
    if tb >= 1:
        return f"{tb:.2f} TB ({bytes_int:,} bytes / {gb:.2f} GB / {mb:.2f} MB)"
    elif gb >= 1:
        return f"{gb:.2f} GB ({bytes_int:,} bytes / {mb:.2f} MB)"
    elif mb >= 1:
        return f"{mb:.2f} MB ({bytes_int:,} bytes / {kb:.2f} KB)"
    elif kb >= 1:
        return f"{kb:.2f} KB ({bytes_int:,} bytes)"
    else:
        return f"{bytes_int:,} B"

def summarize(results):
    if not results:
        return {
            "total_request": 0,
            "success": 0,
            "errors": 0,
            "avg_latency": 0,
            "total_bytes": 0,
            "total_bytes_formatted": "0 B"
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
        "total_bytes": total_bytes,
        "total_bytes_formatted": format_bytes(total_bytes)
    }
