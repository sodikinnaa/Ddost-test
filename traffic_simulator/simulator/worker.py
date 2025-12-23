import time
import requests
import json
from config import REQUEST_TIMEOUT, DEFAULT_METHOD, DEFAULT_HEADERS, DEFAULT_DATA

def run_request(target, proxy, method=None, headers=None, data=None):
    """
    Jalankan custom request ke target
    
    Args:
        target: URL target
        proxy: Proxy string atau None
        method: HTTP method (GET, POST, PUT, DELETE, dll)
        headers: Dictionary headers custom
        data: Data untuk POST/PUT (dict untuk JSON, str untuk raw)
    """
    start = time.time()
    method = method or DEFAULT_METHOD
    headers = headers or DEFAULT_HEADERS.copy()
    data = data if data is not None else DEFAULT_DATA
    
    # Prepare request kwargs
    request_kwargs = {
        "timeout": REQUEST_TIMEOUT,
        "headers": headers
    }
    
    # Add proxy jika ada
    if proxy:
        request_kwargs["proxies"] = {"http": proxy, "https": proxy}
    
    # Add data berdasarkan method
    if method.upper() in ["POST", "PUT", "PATCH"]:
        if isinstance(data, dict):
            request_kwargs["json"] = data
            headers["Content-Type"] = "application/json"
        elif isinstance(data, str):
            request_kwargs["data"] = data
        elif data is not None:
            request_kwargs["data"] = data
    
    try:
        # Execute request berdasarkan method
        method_upper = method.upper()
        if method_upper == "GET":
            r = requests.get(target, **request_kwargs)
        elif method_upper == "POST":
            r = requests.post(target, **request_kwargs)
        elif method_upper == "PUT":
            r = requests.put(target, **request_kwargs)
        elif method_upper == "DELETE":
            r = requests.delete(target, **request_kwargs)
        elif method_upper == "PATCH":
            r = requests.patch(target, **request_kwargs)
        elif method_upper == "HEAD":
            r = requests.head(target, **request_kwargs)
        elif method_upper == "OPTIONS":
            r = requests.options(target, **request_kwargs)
        else:
            # Fallback ke GET jika method tidak dikenal
            r = requests.get(target, **request_kwargs)
        
        latency = time.time() - start
        return r.status_code, latency, len(r.content)
        
    except requests.exceptions.RequestException as e:
        latency = time.time() - start
        return ("ERR", latency, str(e))
    except Exception as e:
        latency = time.time() - start
        return ("ERR", latency, str(e))
