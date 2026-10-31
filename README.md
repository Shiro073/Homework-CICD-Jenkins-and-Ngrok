# python-crud-api

Python REST API sederhana untuk praktikum CI/CD dengan Jenkins, GitHub, Docker, dan ngrok.

## Endpoint

| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Cek status API |
| GET | `/messages` | Lihat semua pesan |
| POST | `/messages` | Tambah pesan, body JSON `{"message": "..."}` |
| DELETE | `/messages?index=N` | Hapus pesan pada index N |

## Menjalankan dengan Docker

```bash
docker build -t python-crud-api:manual .
docker volume create production-api-data
docker run -d --name production-api-container \
  -p 5000:5000 \
  -v production-api-data:/var/lib/backend_data \
  python-crud-api:manual
curl -i http://localhost:5000/health
```

Image punya Docker `HEALTHCHECK` yang memanggil `/health` setiap 30 detik. Statusnya terlihat di `docker ps` sebagai `(healthy)` atau `(unhealthy)`.

## Menjalankan tes

```bash
python -m unittest -v test_app.py
```

Tes menyalakan API di port acak dan menyimpan data di folder sementara, jadi container yang berjalan di port 5000 dan datanya tidak terganggu.

## Pipeline

Jenkins membaca `Jenkinsfile` di root repository. Setiap push ke `main` memicu build lewat GitHub webhook.

| Tahap | Isi |
|---|---|
| 1. Checkout Code | Mengambil kode dari GitHub |
| 2. Code Syntax Verification | `python3 -m py_compile app.py` |
| 2b. Automated Tests | `python3 -m unittest -v test_app.py`. Kalau ada tes yang gagal, tahap 3 sampai 5 dilewati |
| 3. Build Docker Image | Image diberi tag nomor build, `latest`, dan commit SHA pendek |
| 4. Automated Deployment | Container `production-api-container` diganti, data tetap di volume `production-api-data` |
| 5. Health Check | `curl` ke `/health` dari dalam container Jenkins |
