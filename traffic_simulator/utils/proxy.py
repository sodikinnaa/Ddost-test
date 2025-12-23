def load_proxies(path="proxy.txt"):
    try:
        with open(path) as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return []


def save_valid_proxy(proxy, path="proxy_valid.txt"):
    with open(path, "a") as f:
        f.write(proxy + "\n")


def load_valid_proxies(path="proxy_valid.txt"):
    try:
        with open(path) as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return []
