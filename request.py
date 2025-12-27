from concurrent.futures import ThreadPoolExecutor
import requests

url = "https://beraffiliate.com/"

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=200,
    pool_maxsize=200
)
session.mount("https://", adapter)

def tugas(_):
    for _ in range(100):
        try:
            session.get(url, timeout=5)
        except:
            pass

with ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(tugas, range(50))

print("Selesai")
