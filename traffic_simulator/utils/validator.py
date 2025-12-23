import requests
from config import REQUEST_TIMEOUT, ALLOWED_TARGETS

PROXY_TEST_URL = "https://ipv4.webshare.io/"

def validate_target(target):
    """
    Validasi apakah target URL diizinkan berdasarkan ALLOWED_TARGETS
    """
    if not target:
        return False
    
    # Normalisasi target (hapus trailing slash)
    target_clean = target.rstrip('/')
    
    # Cek apakah target ada di daftar yang diizinkan
    for allowed in ALLOWED_TARGETS:
        allowed_clean = allowed.rstrip('/')
        # Cek exact match atau apakah target dimulai dengan allowed
        if target_clean == allowed_clean or target_clean.startswith(allowed_clean + '/'):
            return True
    
    return False

def validate_proxy(proxy, verbose=False):
    """
    Validate proxy dengan melakukan test request menggunakan format curl
    Proxy harus dalam format: http://user:pass@ip:port atau http://ip:port
    
    Test URL: https://ipv4.webshare.io/ (sama seperti curl test)
    
    Args:
        proxy: Proxy string dalam format http://user:pass@ip:port
        verbose: Jika True, return tuple (is_valid, error_message, ip_returned)
    
    Returns:
        bool: True jika valid, False jika tidak
        atau tuple (bool, str, str) jika verbose=True
    """
    if not proxy:
        return (False, "Proxy is empty", None) if verbose else False
    
    # Pastikan proxy dalam format yang benar (tanpa trailing slash)
    proxy_clean = proxy.rstrip('/')
    
    # Extract IP:PORT untuk display
    display_proxy = proxy_clean
    if '@' in proxy_clean:
        parts = proxy_clean.split('@')
        if len(parts) == 2:
            display_proxy = parts[1]
    
    proxies = {
        "http": proxy_clean,
        "https": proxy_clean
    }

    try:
        # Test dengan HTTP proxy ke HTTPS URL (seperti curl)
        r = requests.get(
            PROXY_TEST_URL,
            proxies=proxies,
            timeout=REQUEST_TIMEOUT,
            verify=True  # Verify SSL certificate
        )

        if r.status_code != 200:
            error_msg = f"HTTP {r.status_code}"
            return (False, error_msg, None) if verbose else False

        # Response body harus berupa IP address (IPv4)
        response_text = r.text.strip()
        ip_parts = response_text.split(".")
        
        # Validasi: harus ada 4 bagian (IPv4) dan setiap bagian adalah angka
        if len(ip_parts) != 4:
            error_msg = f"Invalid IP format: {response_text}"
            return (False, error_msg, None) if verbose else False
        
        try:
            # Pastikan setiap bagian adalah angka valid (0-255)
            for part in ip_parts:
                num = int(part)
                if num < 0 or num > 255:
                    error_msg = f"Invalid IP range: {response_text}"
                    return (False, error_msg, None) if verbose else False
            
            # Proxy valid - return IP yang dikembalikan
            return (True, "OK", response_text) if verbose else True
        except ValueError:
            error_msg = f"Invalid IP format: {response_text}"
            return (False, error_msg, None) if verbose else False

    except requests.exceptions.ProxyError as e:
        # Proxy error - proxy tidak valid atau tidak bisa connect
        error_msg = f"ProxyError: {str(e)[:80]}"
        return (False, error_msg, None) if verbose else False
    except requests.exceptions.ConnectTimeout:
        error_msg = "Connection timeout"
        return (False, error_msg, None) if verbose else False
    except requests.exceptions.Timeout:
        error_msg = "Request timeout"
        return (False, error_msg, None) if verbose else False
    except requests.exceptions.SSLError as e:
        # SSL error - coba dengan https:// prefix
        try:
            proxy_https = proxy_clean.replace("http://", "https://")
            proxies_https = {"http": proxy_https, "https": proxy_https}
            r = requests.get(
                PROXY_TEST_URL, 
                proxies=proxies_https, 
                timeout=REQUEST_TIMEOUT,
                verify=False  # Skip SSL verification untuk proxy test
            )
            if r.status_code == 200:
                response_text = r.text.strip()
                ip_parts = response_text.split(".")
                if len(ip_parts) == 4:
                    return (True, "OK (HTTPS)", response_text) if verbose else True
        except Exception as e2:
            error_msg = f"SSL Error (HTTPS fallback failed): {str(e2)[:50]}"
            return (False, error_msg, None) if verbose else False
        error_msg = f"SSL Error: {str(e)[:50]}"
        return (False, error_msg, None) if verbose else False
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: {str(e)[:80]}"
        return (False, error_msg, None) if verbose else False
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)[:80]}"
        return (False, error_msg, None) if verbose else False
