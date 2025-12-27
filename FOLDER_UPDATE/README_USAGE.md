# Cara Menggunakan UPDATE-3_24_2023_PIE.py

⚠️ **PENTING: PERINGATAN HUKUM DAN ETIKA**
- Script ini adalah tool untuk DoS/DDoS attack
- **JANGAN** gunakan pada sistem yang tidak Anda miliki atau tanpa izin eksplisit
- Menggunakan tool ini untuk menyerang sistem orang lain adalah **ILEGAL** dan dapat dituntut hukum
- Gunakan **HANYA** untuk:
  - Testing sistem sendiri
  - Penetration testing dengan izin tertulis
  - Security research dengan izin

## Prerequisites

Pastikan sudah install dependencies:
```bash
pip install colorama
```

## Cara Menjalankan

```bash
python3 FOLDER_UPDATE/UPDATE-3_24_2023_PIE.py
```

Script akan meminta input interaktif:

### 1. TYPE PACKET
```
TYPE PACKET (DEFAULT=PYF EXAMPLE=OWN1)>
```
**Pilihan:**
- `PYF` atau `PY` (default) - Format packet standar
- `OWN1` - Format packet custom 1 (dengan `\r\r` di akhir)
- `OWN2` - Format packet custom 2 (dengan `\r\r\n\n`)
- `OWN3` - Format packet custom 3 (dengan `\n\r\n`)
- `OWN4` - Format packet custom 4 (dengan multiple `\n\n\n\n`)
- `OWN5` - Format packet custom 5 (dengan `\n\n\n\n\r\r\r\r`)

**Contoh input:**
- Tekan Enter untuk default (`PYF`)
- Atau ketik: `OWN1`, `OWN2`, dll

### 2. IP/URL
```
IP/URL>
```
**Input target:**
- IP address: `192.168.1.1`
- Domain: `example.com`
- URL: `https://example.com` (script akan extract domain/IP)

**Contoh:**
```
IP/URL>127.0.0.1
IP/URL>localhost
IP/URL>example.com
```

### 3. PORT
```
PORT>
```
**Input port number:**
- HTTP biasanya: `80`
- HTTPS biasanya: `443`
- Custom port: `8080`, `3000`, dll

**Contoh:**
```
PORT>80
PORT>443
PORT>8000
```

### 4. TIME (Duration)
```
TIME (DEFAULT=250)>
```
**Input duration dalam detik:**
- Berapa lama attack akan berjalan
- Default: `250` detik (4 menit 10 detik)
- Tekan Enter untuk default

**Contoh:**
```
TIME (DEFAULT=250)>60    # 1 menit
TIME (DEFAULT=250)>300   # 5 menit
TIME (DEFAULT=250)>      # 250 detik (default)
```

### 5. SPAM THREAD
```
SPAM THREAD (DEFAULT=50 EXAMPLE=299)>
```
**Input jumlah thread per iteration:**
- Setiap iteration akan create thread sebanyak ini
- Default: `50`
- Semakin besar, semakin banyak request

**Contoh:**
```
SPAM THREAD (DEFAULT=50 EXAMPLE=299)>50
SPAM THREAD (DEFAULT=50 EXAMPLE=299)>100
SPAM THREAD (DEFAULT=50 EXAMPLE=299)>299
```

### 6. CREATE THREAD
```
CREATE THREAD (DEFAULT=50)>
```
**Input jumlah thread utama:**
- Jumlah thread controller yang akan dibuat
- Default: `50`
- Semakin besar, semakin banyak concurrent threads

**Contoh:**
```
CREATE THREAD (DEFAULT=50)>50
CREATE THREAD (DEFAULT=50)>100
CREATE THREAD (DEFAULT=50)>200
```

### 7. BOOTER SENT
```
BOOTER SENT (DEFAULT=500 EXAMPLE=65536)>
```
**Input jumlah packet per connection:**
- Berapa banyak packet yang dikirim per koneksi
- Default: `500`
- Semakin besar, semakin banyak data per connection

**Contoh:**
```
BOOTER SENT (DEFAULT=500 EXAMPLE=65536)>500
BOOTER SENT (DEFAULT=500 EXAMPLE=65536)>1000
BOOTER SENT (DEFAULT=500 EXAMPLE=65536)>65536
```

### 8. HTTP_METHODS
```
HTTP_METHODS (EXAMPLE=GATEWAY)>
```
**Input HTTP method atau custom method:**
- Standard methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`, `TRACE`, `CONNECT`
- Custom methods: `GATEWAY`, `PYFLOODER`, `PANOS`, `MIRAI`, `EXPLOIT`, `LOGSHELL`, `SERVER`, `CLOUDFLARE`, `AGE`

**Contoh:**
```
HTTP_METHODS (EXAMPLE=GATEWAY)>GET
HTTP_METHODS (EXAMPLE=GATEWAY)>POST
HTTP_METHODS (EXAMPLE=GATEWAY)>GATEWAY
HTTP_METHODS (EXAMPLE=GATEWAY)>PYFLOODER
```

### 9. SPAM CREATE THREAD
```
SPAM CREATE THREAD (DEFAULT=5 EXAMPLE=15)>
```
**Input multiplier untuk thread creation:**
- Setiap CREATE THREAD akan dikalikan dengan ini
- Default: `5`
- Total threads = CREATE THREAD × SPAM CREATE THREAD

**Contoh:**
```
SPAM CREATE THREAD (DEFAULT=5 EXAMPLE=15)>5
SPAM CREATE THREAD (DEFAULT=5 EXAMPLE=15)>10
SPAM CREATE THREAD (DEFAULT=5 EXAMPLE=15)>15
```

## Contoh Penggunaan Lengkap

### Contoh 1: Basic Attack
```
TYPE PACKET (DEFAULT=PYF EXAMPLE=OWN1)>PYF
IP/URL>127.0.0.1
PORT>8000
TIME (DEFAULT=250)>60
SPAM THREAD (DEFAULT=50 EXAMPLE=299)>50
CREATE THREAD (DEFAULT=50)>50
BOOTER SENT (DEFAULT=500 EXAMPLE=65536)>500
HTTP_METHODS (EXAMPLE=GATEWAY)>GET
SPAM CREATE THREAD (DEFAULT=5 EXAMPLE=15)>5
```

### Contoh 2: High Intensity Attack
```
TYPE PACKET (DEFAULT=PYF EXAMPLE=OWN1)>OWN1
IP/URL>localhost
PORT>80
TIME (DEFAULT=250)>300
SPAM THREAD (DEFAULT=50 EXAMPLE=299)>299
CREATE THREAD (DEFAULT=50)>200
BOOTER SENT (DEFAULT=500 EXAMPLE=65536)>65536
HTTP_METHODS (EXAMPLE=GATEWAY)>GATEWAY
SPAM CREATE THREAD (DEFAULT=5 EXAMPLE=15)>15
```

### Contoh 3: Custom Method Attack
```
TYPE PACKET (DEFAULT=PYF EXAMPLE=OWN1)>OWN5
IP/URL>example.com
PORT>443
TIME (DEFAULT=250)>120
SPAM THREAD (DEFAULT=50 EXAMPLE=299)>100
CREATE THREAD (DEFAULT=50)>100
BOOTER SENT (DEFAULT=500 EXAMPLE=65536)>1000
HTTP_METHODS (EXAMPLE=GATEWAY)>PYFLOODER
SPAM CREATE THREAD (DEFAULT=5 EXAMPLE=15)>10
```

## Cara Kerja Script

1. **Input Phase**: Script meminta semua parameter
2. **Resolution Phase**: Script resolve IP dari hostname/URL
3. **Thread Creation Phase**: Script membuat thread controller sesuai `CREATE THREAD`
4. **Attack Phase**: 
   - Setiap thread controller membuat multiple attack threads (sesuai `SPAM CREATE THREAD`)
   - Setiap attack thread membuat multiple DoS threads (sesuai `SPAM THREAD`)
   - Setiap DoS thread mengirim packet (sesuai `BOOTER SENT`)
5. **Running Phase**: Attack berjalan selama `TIME` detik
6. **Output Phase**: Script menampilkan status flooding dengan RPS count

## Perhitungan Total Load

**Total Threads:**
```
Total = CREATE THREAD × SPAM CREATE THREAD × SPAM THREAD × 5
```
(×5 karena setiap spam_thread loop membuat 5 threads)

**Contoh:**
- CREATE THREAD = 50
- SPAM CREATE THREAD = 5
- SPAM THREAD = 50
- Total = 50 × 5 × 50 × 5 = **62,500 threads**

**Estimated RPS:**
```
RPS ≈ (Total Threads × BOOTER SENT × 2) / TIME
```
(×2 karena setiap connection mengirim 2x: sendall + send)

## Output

Script akan menampilkan:
- Banner tool
- Status flooding per thread dengan format:
  ```
  FLOODING HTTP ---> TARGET=IP:PORT PATH=PATH_TYPE RPS=COUNT ID=THREAD_ID
  ```
- "TRYING SENT . . ." saat attack berjalan

## Troubleshooting

### Error: "CAN'T IMPORT"
**Solusi:** Install colorama
```bash
pip install colorama
```

### Error: "socket.gaierror"
**Solusi:** 
- Check koneksi internet
- Pastikan hostname/IP valid
- Pastikan DNS resolution bekerja

### Script Tidak Berjalan
**Solusi:**
- Pastikan Python 3 installed
- Check permissions
- Pastikan semua dependencies installed

### Attack Tidak Efektif
**Solusi:**
- Increase CREATE THREAD
- Increase SPAM THREAD
- Increase BOOTER SENT
- Gunakan custom packet type (OWN1-5)
- Gunakan custom HTTP methods

## ⚠️ PERINGATAN PENTING

1. **Legal Issues:**
   - Menggunakan tool ini untuk attack sistem orang lain adalah **ILEGAL**
   - Dapat dituntut dengan pasal cybercrime
   - Risiko penjara dan denda

2. **Ethical Issues:**
   - Mengganggu layanan pihak lain adalah tidak etis
   - Dapat merugikan banyak orang
   - Melanggar ToS dari ISP/server

3. **Technical Issues:**
   - Tool ini sangat resource intensive
   - Dapat membuat sistem Anda sendiri hang/crash
   - Dapat membanjiri bandwidth Anda sendiri

4. **Best Practice:**
   - Gunakan HANYA pada sistem sendiri
   - Gunakan dalam environment terkontrol
   - Monitor resource usage
   - Stop segera jika ada masalah

## Alternatif yang Lebih Aman

Jika Anda ingin melakukan **load testing** yang legitimate, gunakan:
- **Traffic Simulator** (ada di folder `traffic_simulator/`)
- **Apache Bench (ab)**
- **wrk**
- **JMeter**
- **Locust**

Tools tersebut lebih aman, profesional, dan memiliki safety guards.

## Kesimpulan

Script ini adalah tool yang sangat powerful namun berbahaya. Gunakan dengan **sangat hati-hati** dan **hanya pada sistem yang Anda miliki**. Selalu ingat konsekuensi hukum dan etika.

