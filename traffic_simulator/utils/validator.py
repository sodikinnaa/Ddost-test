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

def validate_proxy(proxy):
    proxies = {
        "http": proxy,
        "https": proxy
    }

    try:
        r = requests.get(
            PROXY_TEST_URL,
            proxies=proxies,
            timeout=REQUEST_TIMEOUT
        )

        if r.status_code != 200:
            return False

        # body harus IP (basic sanity check)
        ip = r.text.strip()
        return len(ip.split(".")) == 4

    except requests.exceptions.ProxyError:
        return False
    except requests.exceptions.ConnectTimeout:
        return False
    except Exception:
        return False
