import threading
import time
import requests

url = "https://beraffiliate.com/"

def tugas(nama):
    for i in range(100):
        response = requests.get(url)
        print(f"{nama} jalan ke-{i} {response.status_code}")

threads = []

# buat & start thread
for i in range(10):
    t1 = threading.Thread(target=tugas, args=(f"Thread-1-{i}",))
    t2 = threading.Thread(target=tugas, args=(f"Thread-2-{i}",))

    t1.start()
    t2.start()

    threads.append(t1)
    threads.append(t2)

# tunggu semua thread selesai
for t in threads:
    t.join()

print("Semua thread selesai")
