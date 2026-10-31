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

## Pipeline

Jenkins membaca `Jenkinsfile` di root repository: checkout, cek sintaks Python, build image Docker, deploy container, lalu health check.

Webhook test: 2026-10-31
