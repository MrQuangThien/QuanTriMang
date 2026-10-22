# Network AutoManager

Hệ thống Python/FastAPI tự động sao lưu và quản lý cấu hình thiết bị mạng.

## Chức năng

1. Quản lý nhiều thiết bị bằng YAML.
2. Kết nối SSH bằng Netmiko cho thiết bị thông thường.
3. Fallback OpenSSH legacy cho Cisco IOS cũ trong GNS3.
4. Backup `show running-config` theo timestamp.
5. Backup nhiều thiết bị song song.
6. Lưu lịch sử backup vào SQLite.
7. Git versioning cho thư mục backup.
8. Phát hiện thay đổi giữa hai backup gần nhất.
9. Xem unified diff.
10. Restore có bước `confirm=true`.
11. Theo dõi CPU/RAM/nhiệt độ cơ bản.
12. Kiểm tra GNS3 API.
13. Dashboard + Swagger API.

## Cấu trúc

```text
network_automanager/
├── config/
├── core/
├── storage/
├── api/
├── web/
├── backups/
├── logs/
├── tests/
├── app.py
└── requirements.txt
```

## Chạy trên Windows

```powershell
cd E:\QUANTRIMANGSP\network_automanager
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Web:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## R1 hiện tại

R1 lab:
- IP: `192.168.56.201`
- username: `admin`
- password: `Admin@123`
- SSH legacy: group1 + aes128-cbc + ssh-rsa

Nếu chạy service trên Ubuntu:

```bash
sudo apt update
sudo apt install -y sshpass
```

Sau đó kiểm tra:

```bash
ssh \
-o KexAlgorithms=+diffie-hellman-group1-sha1 \
-o Ciphers=+aes128-cbc \
-o HostKeyAlgorithms=+ssh-rsa \
-o PubkeyAcceptedAlgorithms=+ssh-rsa \
admin@192.168.56.201
```

## API

Backup tất cả:

```powershell
curl -X POST http://127.0.0.1:8000/api/backup
```

Backup R1:

```powershell
curl -X POST "http://127.0.0.1:8000/api/backup?device=R1"
```

Lịch sử:

```text
GET /api/backup
```

Diff:

```text
GET /api/diff/R1
```

Metric:

```text
GET /api/metrics/R1
```

GNS3:

```text
GET /api/gns3
GET /api/gns3/projects
```

Restore:

```text
POST /api/restore?device=R1&backup_file=...&confirm=true
```

## Lưu ý

Restore sẽ thay đổi cấu hình thiết bị. Chỉ thử trong lab và luôn backup trước khi restore.

Không commit `.env` hoặc backup cấu hình chứa thông tin nhạy cảm vào repository công khai.

## Ubuntu Agent (Windows FastAPI -> Ubuntu -> R1)

R1 uses legacy SSH and is reachable from Ubuntu. The Windows FastAPI service therefore delegates legacy commands to an Ubuntu Agent on port 9000.

### Ubuntu
```bash
cd ~/network_automanager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo apt update
sudo apt install -y sshpass
python -m uvicorn agent:app --host 0.0.0.0 --port 9000
```

Test from Ubuntu:
```bash
curl http://127.0.0.1:9000/health
```

### Windows
`.env` must contain:
```env
UBUNTU_AGENT_URL=http://192.168.56.102:9000
AGENT_TOKEN=network-lab-token
```

Test from Windows:
```powershell
curl.exe http://192.168.56.102:9000/health
```

Then run the main application:
```powershell
python app.py
```

The backup flow becomes:
`Browser -> Windows FastAPI -> Ubuntu Agent -> sshpass -> R1 -> backup file -> SQLite/Git/Diff`.
