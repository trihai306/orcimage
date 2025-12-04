# Hướng dẫn Deploy OCR Server lên aaPanel

## Yêu cầu hệ thống

- Server Linux (Ubuntu/CentOS/Debian)
- aaPanel đã được cài đặt
- Python 3.8+ trên server
- Domain hoặc IP public (tùy chọn)

## Bước 1: Chuẩn bị trên aaPanel

### 1.1. Tạo Website trong aaPanel

1. Đăng nhập vào aaPanel
2. Vào **Website** → **Add Site**
3. Nhập domain hoặc IP của bạn
4. Chọn **Python Project** (nếu có) hoặc **PHP** (sẽ đổi sau)
5. Click **Submit**

### 1.2. Cài đặt Python Manager (nếu chưa có)

1. Vào **App Store** trong aaPanel
2. Tìm và cài đặt **Python Project Manager** hoặc **PM2 Manager**
3. Hoặc sử dụng **Terminal** có sẵn trong aaPanel

## Bước 2: Upload code lên server

### 2.1. Cách 1: Upload qua File Manager

1. Vào **File** → **File Manager** trong aaPanel
2. Navigate đến thư mục website vừa tạo (thường là `/www/wwwroot/your-domain.com`)
3. Upload toàn bộ code dự án vào thư mục này:
   - `app/` folder
   - `requirements.txt`
   - `README.md`

### 2.2. Cách 2: Upload qua Git (Khuyến nghị)

```bash
# SSH vào server
ssh root@your-server-ip

# Vào thư mục website
cd /www/wwwroot/your-domain.com

# Clone repository (nếu có)
git clone your-repo-url .

# Hoặc tạo thư mục mới
mkdir ocr-server
cd ocr-server
# Upload files vào đây
```

## Bước 3: Cài đặt Python và Dependencies

### 3.1. Kiểm tra Python version

```bash
python3 --version
# Nếu chưa có, cài đặt:
# Ubuntu/Debian:
apt update && apt install python3 python3-pip python3-venv -y

# CentOS:
yum install python3 python3-pip -y
```

### 3.2. Tạo Virtual Environment

```bash
cd /www/wwwroot/your-domain.com
python3 -m venv venv
source venv/bin/activate
```

### 3.3. Cài đặt Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Lưu ý:** EasyOCR sẽ tự động tải model lần đầu, có thể mất vài phút.

## Bước 4: Cấu hình PM2 để chạy ứng dụng

### 4.1. Tạo file start script

Tạo file `start.sh` trong thư mục dự án:

```bash
#!/bin/bash
cd /www/wwwroot/your-domain.com
source venv/bin/activate
python -m app.main
```

Cấp quyền thực thi:
```bash
chmod +x start.sh
```

### 4.2. Sử dụng PM2 Manager trong aaPanel

1. Vào **App Store** → Cài **PM2 Manager** (nếu chưa có)
2. Vào **PM2 Manager**
3. Click **Add** → **Add Node App**
4. Điền thông tin:
   - **App Name:** `ocr-server`
   - **Run Path:** `/www/wwwroot/your-domain.com`
   - **Startup File:** `app/main.py`
   - **Interpreter:** `/www/wwwroot/your-domain.com/venv/bin/python`
   - **Port:** `8000` (hoặc port khác)
   - **Options:** `-m app.main`

### 4.3. Hoặc sử dụng PM2 qua Terminal

```bash
# Cài đặt PM2 global
npm install -g pm2

# Vào thư mục dự án
cd /www/wwwroot/your-domain.com

# Tạo file ecosystem.config.js
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'ocr-server',
    script: 'venv/bin/python',
    args: '-m app.main',
    cwd: '/www/wwwroot/your-domain.com',
    interpreter: 'none',
    env: {
      PORT: 8000
    }
  }]
}
EOF

# Start với PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Bước 5: Cấu hình Nginx Reverse Proxy

### 5.1. Tạo Nginx config

1. Vào **Website** → Chọn website của bạn → **Settings**
2. Vào tab **Configuration**
3. Thêm hoặc sửa config như sau:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Logs
    access_log /www/wwwlogs/your-domain.com.log;
    error_log /www/wwwlogs/your-domain.com.error.log;
    
    # Upload size limit (cho ảnh lớn)
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (nếu cần)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Static files (nếu có)
    location /static {
        alias /www/wwwroot/your-domain.com/static;
    }
}
```

4. Click **Save** và **Reload** Nginx

### 5.2. Hoặc sử dụng aaPanel Website Settings

1. Vào **Website** → Chọn website → **Settings**
2. Vào **Reverse Proxy**
3. Thêm reverse proxy:
   - **Proxy Name:** `ocr-api`
   - **Target URL:** `http://127.0.0.1:8000`
   - **Send Domain:** Bật
   - **WebSocket:** Tắt (hoặc bật nếu cần)

## Bước 6: Cấu hình Firewall

### 6.1. Mở port trong aaPanel

1. Vào **Security** → **Firewall**
2. Thêm rule:
   - **Port:** `8000` (hoặc port bạn chọn)
   - **Protocol:** TCP
   - **Action:** Allow

### 6.2. Hoặc sử dụng Terminal

```bash
# Ubuntu/Debian
ufw allow 8000/tcp

# CentOS
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
```

## Bước 7: Cấu hình SSL (HTTPS) - Tùy chọn

1. Vào **Website** → Chọn website → **Settings**
2. Vào tab **SSL**
3. Chọn **Let's Encrypt** (miễn phí)
4. Nhập email và click **Apply**
5. Bật **Force HTTPS**

## Bước 8: Kiểm tra và Test

### 8.1. Kiểm tra PM2 status

```bash
pm2 status
pm2 logs ocr-server
```

### 8.2. Test API

```bash
# Test health endpoint
curl http://your-domain.com/health

# Test OCR endpoint
curl -X POST "http://your-domain.com/ocr" \
  -F "file=@test-image.jpg"
```

### 8.3. Kiểm tra logs

```bash
# PM2 logs
pm2 logs ocr-server

# Nginx logs
tail -f /www/wwwlogs/your-domain.com.log
tail -f /www/www/wwwlogs/your-domain.com.error.log

# Application logs (nếu có)
tail -f /www/wwwroot/your-domain.com/logs/app.log
```

## Bước 9: Tối ưu hóa

### 9.1. Tăng workers cho Uvicorn

Sửa file `app/main.py` hoặc tạo file `start.sh`:

```bash
#!/bin/bash
cd /www/wwwroot/your-domain.com
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 9.2. Cấu hình PM2 với nhiều instances

Sửa `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'ocr-server',
    script: 'venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000 --workers 2',
    instances: 2,
    exec_mode: 'cluster',
    cwd: '/www/wwwroot/your-domain.com',
    env: {
      PORT: 8000
    }
  }]
}
```

### 9.3. Tự động restart khi server reboot

```bash
pm2 save
pm2 startup
# Chạy lệnh được hiển thị để cấu hình startup
```

## Troubleshooting

### Lỗi: Port đã được sử dụng

```bash
# Tìm process đang dùng port 8000
lsof -i :8000
# Hoặc
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>
```

### Lỗi: Permission denied

```bash
# Cấp quyền cho thư mục
chown -R www:www /www/wwwroot/your-domain.com
chmod -R 755 /www/wwwroot/your-domain.com
```

### Lỗi: EasyOCR không tải được model

```bash
# Kiểm tra kết nối internet
ping google.com

# Tải model thủ công (nếu cần)
# EasyOCR sẽ tự động tải khi chạy lần đầu
```

### Lỗi: Memory không đủ

```bash
# Kiểm tra memory
free -h

# Giảm số workers nếu cần
# Sửa workers trong start script từ 4 xuống 2 hoặc 1
```

## Cấu trúc thư mục trên server

```
/www/wwwroot/your-domain.com/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── ocr_service.py
│   └── models.py
├── uploads/          # Tự động tạo
├── venv/             # Virtual environment
├── requirements.txt
├── ecosystem.config.js
├── start.sh
└── README.md
```

## Lệnh hữu ích

```bash
# Restart PM2 app
pm2 restart ocr-server

# Stop PM2 app
pm2 stop ocr-server

# Start PM2 app
pm2 start ocr-server

# Xem logs realtime
pm2 logs ocr-server --lines 100

# Reload Nginx
nginx -s reload
# Hoặc trong aaPanel: Website → Settings → Reload

# Kiểm tra port
netstat -tulpn | grep 8000
```

## Liên kết hữu ích

- aaPanel Documentation: https://doc.aapanel.com/
- PM2 Documentation: https://pm2.keymetrics.io/
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. PM2 logs: `pm2 logs ocr-server`
2. Nginx error logs: `/www/wwwlogs/your-domain.com.error.log`
3. Server resources: `htop` hoặc `free -h`
4. Network connectivity: `curl http://localhost:8000/health`

