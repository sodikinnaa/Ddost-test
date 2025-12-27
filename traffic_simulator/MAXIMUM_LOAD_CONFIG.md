# Maximum Load Configuration Guide

⚠️ **PENTING: Dokumentasi ini hanya untuk INTERNAL TESTING pada lingkungan yang Anda miliki/kontrol!**

## ⚠️ Safety Warning

Tool ini dirancang dengan **safety guards** untuk mencegah abuse. Konfigurasi maksimal saat ini:

- **Max RPS**: 1,000 req/s (hard limit)
- **Max Concurrent**: 500 connections (hard limit)
- **Target Validation**: Hanya internal/staging IPs yang diizinkan

## Konfigurasi Maksimal Saat Ini

### 1. Melalui CLI (Interactive)

Saat menjalankan `python main.py`, gunakan nilai maksimal:

```
Target URL: http://localhost:8000  (atau internal target Anda)
HTTP Method: GET
Max Concurrent Users: 500  (maksimal yang diizinkan)
Target RPS: 1000  (maksimal yang diizinkan)
Duration: [sesuai kebutuhan]
Ramp-up time: 5  (minimal untuk cepat mencapai target)
Ramp-down time: 5
Traffic Pattern: 1 (Steady) - untuk load konsisten
```

### 2. Modifikasi Config untuk Load Testing Ekstrem

**⚠️ HATI-HATI: Hanya lakukan ini untuk internal testing yang legitimate!**

Jika Anda perlu load testing lebih ekstrem (misalnya untuk stress testing internal server), Anda bisa memodifikasi:

#### File: `config.py`

```python
# Untuk load testing ekstrem - HANYA UNTUK INTERNAL TESTING!
MAX_RPS_LIMIT = 5000  # Naikkan dari 1000 ke 5000 req/s
MAX_CONCURRENT_CONNECTIONS = 2000  # Naikkan dari 500 ke 2000

# Timeout lebih pendek untuk throughput lebih tinggi
REQUEST_TIMEOUT = 10  # Kurangi dari 30 ke 10 seconds

# Think time minimal untuk generate lebih banyak requests
DEFAULT_THINK_TIME_MIN = 0.1  # Kurangi dari 0.5 ke 0.1 seconds
DEFAULT_THINK_TIME_MAX = 0.5  # Kurangi dari 2.0 ke 0.5 seconds
```

#### File: `simulator/safety.py`

```python
# Untuk load testing ekstrem - HANYA UNTUK INTERNAL TESTING!
MAX_RPS_LIMIT = 5000  # Naikkan dari 1000
MAX_CONCURRENT_CONNECTIONS = 2000  # Naikkan dari 500
```

### 3. Konfigurasi Traffic Pattern untuk Maximum Load

Gunakan **Steady Pattern** untuk load konsisten maksimal:

```python
# Pattern: Steady
# Target RPS: 1000 (atau nilai maksimal yang diizinkan)
# Ramp-up: Minimal (5 seconds)
# Ramp-down: Minimal (5 seconds)
```

Atau gunakan **Burst Pattern** untuk spike testing:

```python
# Pattern: Burst
# Base RPS: 500
# Burst RPS: 2000 (jika limit dinaikkan)
# Burst Duration: 5 seconds
# Burst Interval: 10 seconds
```

### 4. Optimasi untuk Maximum Throughput

#### Kurangi Think Time Virtual Users

Edit `simulator/virtual_user.py` atau pass parameters:

```python
think_time_min=0.1  # Minimal delay
think_time_max=0.2  # Maksimal delay kecil
```

#### Shorten Session Duration

```python
session_duration_min=10  # Session lebih pendek = lebih banyak requests
session_duration_max=30
```

### 5. Multiple Instances (Advanced)

Untuk load testing ekstrem, Anda bisa menjalankan beberapa instance secara paralel:

```bash
# Terminal 1
python main.py  # Instance 1

# Terminal 2  
python main.py  # Instance 2

# Terminal 3
python main.py  # Instance 3
```

**Total Load**: Masing-masing instance bisa generate hingga 1000 req/s
**Combined**: 3000+ req/s (jika 3 instances)

## Perkiraan Load yang Bisa Dihasilkan

### Dengan Setting Default (Safety Guards Aktif)
- **RPS**: Up to 1,000 req/s
- **Concurrent**: Up to 500 connections
- **Suitable for**: Testing server dengan specs rendah-sedang

### Dengan Config Modified (Ekstrem)
- **RPS**: Up to 5,000+ req/s
- **Concurrent**: Up to 2,000 connections
- **Suitable for**: Stress testing server high-spec

### Dengan Multiple Instances
- **RPS**: 5,000 - 15,000+ req/s (tergantung jumlah instances)
- **Suitable for**: Load testing sangat ekstrem

## ⚠️ Considerations

1. **Server Resources**: Pastikan server target mampu handle load yang di-generate
2. **Network Bandwidth**: Load tinggi akan consume bandwidth signifikan
3. **Client Resources**: Tool ini juga akan consume CPU/RAM di sisi client
4. **Monitoring**: Monitor server metrics (CPU, RAM, network, response time) selama testing
5. **Gradual Increase**: Jangan langsung dari 0 ke max - gunakan ramp-up yang gradual

## Best Practices untuk Load Testing Ekstrem

1. **Start Small**: Mulai dengan load kecil, naikkan bertahap
2. **Monitor Server**: Monitor server metrics real-time
3. **Stop Immediately**: Jika server mulai tidak responsif, stop test segera
4. **Document Results**: Catat metrics untuk analisis
5. **Test in Isolation**: Pastikan tidak ada service lain yang terpengaruh
6. **Backup First**: Backup data/config penting sebelum testing

## Contoh Workflow untuk Stress Testing

1. **Phase 1 - Baseline**:
   - RPS: 100 req/s, Duration: 60s
   - Observe server behavior

2. **Phase 2 - Medium Load**:
   - RPS: 500 req/s, Duration: 120s
   - Observe server behavior

3. **Phase 3 - High Load**:
   - RPS: 1000 req/s, Duration: 180s
   - Observe server behavior

4. **Phase 4 - Extreme Load** (jika config dimodifikasi):
   - RPS: 2000-5000 req/s, Duration: 300s
   - Monitor carefully, stop jika diperlukan

## ⚠️ Legal & Ethical Notice

**PENTING**: 
- Tool ini hanya untuk testing pada sistem yang **Anda miliki** atau memiliki **izin eksplisit** untuk test
- **JANGAN** gunakan pada production tanpa izin
- **JANGAN** gunakan pada sistem pihak ketiga tanpa izin
- Melanggar sistem orang lain adalah **ilegal** dan dapat dituntut hukum

## Kesimpulan

Settingan maksimal **default** (dengan safety guards):
- **RPS**: 1,000 req/s
- **Concurrent**: 500 connections

Untuk load testing **lebih ekstrem**, Anda bisa:
1. Modifikasi config files (naikkan limits)
2. Gunakan multiple instances
3. Optimasi think time dan session duration
4. Gunakan burst pattern untuk spike testing

**Selalu ingat**: Load testing ekstrem dapat membuat server menjadi tidak responsif atau down. Lakukan hanya pada environment yang Anda kontrol dan siap untuk handle consequences.

