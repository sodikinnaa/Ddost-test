def parse_proxy(proxy_str):
    """
    Parse proxy string ke format yang digunakan oleh requests/curl
    
    Format yang didukung:
    - IP:PORT:USERNAME:PASSWORD -> http://username:password@ip:port
    - IP:PORT -> http://ip:port
    - http://ip:port (sudah dalam format URL)
    - http://user:pass@ip:port (sudah dalam format URL dengan auth)
    
    Contoh: 142.111.67.146:5611:yciaalgj:z8h1v3ja476u
    Hasil: http://yciaalgj:z8h1v3ja476u@142.111.67.146:5611
    """
    if not proxy_str:
        return None
    
    proxy_str = proxy_str.strip()
    
    # Hapus trailing slash jika ada
    proxy_str = proxy_str.rstrip('/')
    
    # Jika sudah dalam format URL, pastikan format benar
    if proxy_str.startswith(('http://', 'https://', 'socks5://')):
        # Hapus trailing slash dan return
        return proxy_str.rstrip('/')
    
    # Parse format IP:PORT:USERNAME:PASSWORD
    # Split dengan limit untuk handle password yang mungkin mengandung ':'
    # Format: IP:PORT:USERNAME:PASSWORD
    # Kita split 3 kali untuk mendapatkan 4 bagian
    parts = proxy_str.split(':', 3)
    
    if len(parts) == 4:
        # Format: IP:PORT:USERNAME:PASSWORD
        ip, port, username, password = parts
        # Pastikan tidak ada karakter yang tidak valid
        ip = ip.strip()
        port = port.strip()
        username = username.strip()
        password = password.strip()
        
        # Validasi basic
        if not ip or not port or not username or not password:
            return None
        
        # Format: http://username:password@ip:port (sesuai format curl)
        return f"http://{username}:{password}@{ip}:{port}"
    elif len(parts) == 2:
        # Format: IP:PORT (tanpa auth)
        ip, port = parts
        ip = ip.strip()
        port = port.strip()
        
        if not ip or not port:
            return None
        
        return f"http://{ip}:{port}"
    else:
        # Format tidak dikenal
        return None

def load_proxies(path="proxy.txt"):
    """
    Load proxies dari file dan parse ke format yang benar
    Format output: http://username:password@ip:port
    
    Mencoba beberapa variasi nama file:
    - proxy.txt
    -  proxy.txt (dengan spasi di depan)
    - proxy.txt (dengan spasi di belakang)
    """
    import os
    
    # List kemungkinan nama file
    possible_paths = [
        path,
        path.strip(),
        " proxy.txt",  # Dengan spasi di depan
        "proxy.txt ",  # Dengan spasi di belakang
        " proxy.txt ",  # Dengan spasi di depan dan belakang
    ]
    
    # Cari file yang ada
    file_found = None
    for possible_path in possible_paths:
        if os.path.exists(possible_path):
            file_found = possible_path
            break
    
    if not file_found:
        # Coba cari file yang mengandung "proxy" di nama
        current_dir = os.path.dirname(path) if os.path.dirname(path) else "."
        if os.path.exists(current_dir):
            try:
                for filename in os.listdir(current_dir):
                    if "proxy" in filename.lower() and filename.endswith(".txt"):
                        file_found = os.path.join(current_dir, filename)
                        print(f"    [DEBUG] Found proxy file with auto-search: {file_found}")
                        break
            except Exception as e:
                print(f"    [DEBUG] Error listing directory: {e}")
    
    if not file_found:
        print(f"    [ERROR] Could not find proxy.txt file")
        print(f"    [DEBUG] Tried paths: {possible_paths}")
        print(f"    [DEBUG] Current directory: {os.getcwd()}")
        return []
    
    try:
        print(f"    [DEBUG] Loading proxies from: {file_found}")
        with open(file_found, 'r', encoding='utf-8') as f:
            proxies = []
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines dan comments
                    parsed = parse_proxy(line)
                    if parsed:
                        proxies.append(parsed)
                    else:
                        # Log warning jika parsing gagal
                        print(f"    [WARNING] Line {line_num}: Failed to parse proxy format: {line[:50]}")
            return proxies
    except FileNotFoundError:
        print(f"    [ERROR] File not found: {file_found}")
        return []
    except Exception as e:
        print(f"    [ERROR] Error reading file {file_found}: {str(e)}")
        return []


def save_valid_proxy(proxy, path="proxy_valid.txt"):
    """
    Save proxy yang valid ke file
    Proxy disimpan dalam format original jika memungkinkan, atau format yang sudah diparse
    """
    with open(path, "a") as f:
        f.write(proxy + "\n")


def load_valid_proxies(path="proxy_valid.txt"):
    """
    Load proxies yang sudah divalidasi
    Proxy sudah dalam format yang benar (http://user:pass@ip:port)
    """
    try:
        with open(path) as f:
            proxies = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines dan comments
                    # Pastikan format benar, parse jika perlu
                    parsed = parse_proxy(line)
                    if parsed:
                        proxies.append(parsed)
            return proxies
    except FileNotFoundError:
        return []
