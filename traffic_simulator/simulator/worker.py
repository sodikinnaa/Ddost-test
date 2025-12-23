import time
import requests
import json
import random
from config import REQUEST_TIMEOUT, DEFAULT_METHOD, DEFAULT_HEADERS, DEFAULT_DATA, BRUTAL_REQUEST_TIMEOUT

# User agents untuk variasi (anti-detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

def run_request(target, proxy, method=None, headers=None, data=None, brutal_mode=False):
    """
    Jalankan custom request ke target
    
    Args:
        target: URL target
        proxy: Proxy string atau None
        method: HTTP method (GET, POST, PUT, DELETE, dll)
        headers: Dictionary headers custom
        data: Data untuk POST/PUT (dict untuk JSON, str untuk raw)
        brutal_mode: Jika True, mode brutal dengan timeout pendek dan variasi UA
    """
    start = time.time()
    method = method or DEFAULT_METHOD
    headers = headers or DEFAULT_HEADERS.copy()
    data = data if data is not None else DEFAULT_DATA
    
    # Brutal mode: variasi user agent dan timeout pendek
    if brutal_mode:
        headers["User-Agent"] = random.choice(USER_AGENTS)
        timeout = BRUTAL_REQUEST_TIMEOUT
        # Don't wait for full response
        stream = True
    else:
        timeout = REQUEST_TIMEOUT
        stream = False
    
    # Prepare request kwargs
    request_kwargs = {
        "timeout": timeout,
        "headers": headers,
        "stream": stream  # Stream untuk brutal mode (don't wait full response)
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
        
        # Brutal mode: fire and forget - send request tanpa menunggu response lengkap
        if brutal_mode and stream:
            # Untuk brutal mode, kirim request dan langsung close tanpa membaca response
            try:
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
                    r = requests.get(target, **request_kwargs)
                
                # Untuk brutal mode, kita tetap perlu track bytes untuk statistik
                # Tapi jangan menunggu response lengkap - baca header dan sebagian content
                try:
                    # Get status code dulu
                    status_code = r.status_code if hasattr(r, 'status_code') else 200
                    
                    # Track bytes dari Content-Length header jika ada
                    content_length = 0
                    if hasattr(r, 'headers') and 'Content-Length' in r.headers:
                        try:
                            content_length = int(r.headers['Content-Length'])
                        except:
                            pass
                    
                    # Jika tidak ada Content-Length, coba baca sedikit response
                    if content_length == 0:
                        content_chunk = b''
                        if hasattr(r, 'iter_content'):
                            # Baca beberapa chunk untuk estimasi
                            chunk_count = 0
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    content_chunk += chunk
                                    chunk_count += 1
                                # Hanya baca 8 chunks (64KB) untuk estimasi, lalu close
                                if chunk_count >= 8 or len(content_chunk) >= 65536:
                                    # Estimasi total berdasarkan chunk yang terbaca
                                    if chunk_count > 0:
                                        # Asumsikan setiap chunk sekitar 8KB, multiply
                                        content_length = len(content_chunk) * 2  # Estimasi konservatif
                                    break
                        elif hasattr(r, 'content'):
                            content_chunk = r.content[:8192]  # Ambil 8KB pertama
                            content_length = len(content_chunk) * 10  # Estimasi
                    
                    r.close()
                    latency = time.time() - start
                    return status_code, latency, content_length
                except Exception as e:
                    # Jika error, close dan return dengan estimasi minimal
                    try:
                        r.close()
                    except:
                        pass
                    latency = time.time() - start
                    # Return estimasi minimal untuk brutal mode (request terkirim)
                    return 200, latency, 1024  # Minimum 1KB per request
            except:
                # Jika error, anggap request terkirim (brutal mode tidak peduli error)
                latency = time.time() - start
                return 200, latency, 0
        else:
            # Normal mode: wait for full response
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
            content_len = len(r.content) if hasattr(r, 'content') else 0
            return r.status_code, latency, content_len
        
    except requests.exceptions.RequestException as e:
        latency = time.time() - start
        return ("ERR", latency, str(e))
    except Exception as e:
        latency = time.time() - start
        return ("ERR", latency, str(e))
