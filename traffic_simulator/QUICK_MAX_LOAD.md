# Quick Guide: Settingan Maksimal untuk Load Testing Ekstrem

## ⚠️ PENTING: Hanya untuk Internal Testing!

## Settingan Maksimal Default (Dengan Safety Guards)

Saat menjalankan `python main.py`:

```
Max Concurrent Users: 500
Target RPS: 1000
Traffic Pattern: 1 (Steady)
Ramp-up: 5 seconds
Ramp-down: 5 seconds
```

**Load yang dihasilkan**: ~1,000 requests/second dengan 500 concurrent connections

## Untuk Load Lebih Ekstrem

### Opsi 1: Modifikasi Config File

Edit `config.py`:

```python
MAX_RPS_LIMIT = 5000  # Naikkan dari 1000
MAX_CONCURRENT_CONNECTIONS = 2000  # Naikkan dari 500
```

Edit `simulator/safety.py`:

```python
MAX_RPS_LIMIT = 5000  # Naikkan dari 1000
MAX_CONCURRENT_CONNECTIONS = 2000  # Naikkan dari 500
```

### Opsi 2: Multiple Instances

Jalankan beberapa instance secara bersamaan:

```bash
# Terminal 1
python main.py  # 1000 req/s

# Terminal 2
python main.py  # 1000 req/s

# Terminal 3
python main.py  # 1000 req/s
```

**Total**: 3000+ req/s

### Opsi 3: Optimasi Timeout & Think Time

Edit `config.py`:

```python
REQUEST_TIMEOUT = 5  # Kurangi dari 30 ke 5
DEFAULT_THINK_TIME_MIN = 0.05  # Minimal delay
DEFAULT_THINK_TIME_MAX = 0.1   # Maksimal delay kecil
```

## Perkiraan Load

| Config | RPS | Concurrent | Keterangan |
|--------|-----|------------|------------|
| Default | 1,000 | 500 | Safe, dengan safety guards |
| Modified | 5,000 | 2,000 | Ekstrem, untuk stress test |
| Multiple (3x) | 3,000+ | 1,500+ | Combine instances |

## ⚠️ Warning

1. Load tinggi dapat membuat server menjadi tidak responsif atau down
2. Monitor server metrics (CPU, RAM, network) selama testing
3. Hanya gunakan pada sistem yang Anda kontrol
4. Mulai dari load kecil, naikkan bertahap
5. Stop segera jika server mulai tidak responsif

## Lihat Juga

Untuk detail lengkap, lihat: `MAXIMUM_LOAD_CONFIG.md`

