# Hướng dẫn Deploy OCR Server lên aaPanel

Hướng dẫn chi tiết để deploy ứng dụng OCR ID Card Server lên server sử dụng aaPanel.

## Yêu cầu

- Server Linux (Ubuntu/CentOS) với aaPanel đã cài đặt
- Domain đã trỏ về IP server (hoặc sử dụng IP trực tiếp)
- Quyền root hoặc sudo
- Tối thiểu 2GB RAM (khuyến nghị 4GB+)
- 10GB+ dung lượng ổ cứng (để cài đặt Python, dependencies và models)

## Bước 1: Chuẩn bị môi trường trên aaPanel

### 1.1. Cài đặt Python và các công cụ cần thiết

1. Đăng nhập vào aaPanel
2. Vào **App Store** → Tìm và cài đặt:
   - **Python Project Manager** (hoặc Python 3.x)
   - **PM2 Manager** (để quản lý process)
   - **Nginx** (nếu chưa có)

### 1.2. Tạo Website mới

1. Vào **Website** → **Add Site**
2. Điền thông tin:
   - **Domain**: `your-domain.com` (hoặc IP của server)
   - **Root Directory**: `/www/wwwroot/your-domain.com`
   - **PHP Version**: Không cần (chọn None hoặc không chọn)
3. Click **Submit**

## Bước 2: Upload code lên server

### 2.1. Upload files qua File Manager

1. Vào **File** trong aaPanel
2. Điều hướng đến `/www/wwwroot/your-domain.com`
3. Upload tất cả files của dự án (hoặc clone từ Git):

```bash
# Nếu có SSH access, có thể clone trực tiếp:
cd /www/wwwroot/your-domain.com
git clone <your-repo-url> .
```

### 2.2. Cấu trúc thư mục sau khi upload

```
/www/wwwroot/your-domain.com/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── ocr_service.py
├── uploads/
├── requirements.txt
├── start.sh
├── ecosystem.config.js
└── nginx.conf.example
```

## Bước 3: Cài đặt Python và Virtual Environment

### 3.1. Kiểm tra Python version

Mở **Terminal** trong aaPanel hoặc SSH vào server:

```bash
python3 --version
# Hoặc
python --version
```

Cần Python 3.8 trở lên. Nếu chưa có, cài đặt:

```bash
# Ubuntu/Debian
apt update
apt install python3 python3-pip python3-venv -y

# CentOS
yum install python3 python3-pip -y
```

### 3.2. Tạo Virtual Environment

```bash
cd /www/wwwroot/your-domain.com
python3 -m venv venv
```

### 3.3. Activate virtual environment và cài đặt dependencies

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Lưu ý quan trọng:**
- Lần đầu cài đặt EasyOCR sẽ tự động tải các model (có thể mất 5-10 phút)
- Quá trình này cần kết nối internet ổn định
- Dung lượng model khoảng 1-2GB

## Bước 4: Cấu hình PM2 để chạy ứng dụng

### 4.1. Cài đặt PM2 (nếu chưa có)

```bash
npm install -g pm2
```

### 4.2. Chỉnh sửa file ecosystem.config.js

Mở file `ecosystem.config.js` và thay đổi đường dẫn:

```bash
cd /www/wwwroot/your-domain.com
nano ecosystem.config.js
```

Thay đổi dòng:
```javascript
cwd: '/www/wwwroot/your-domain.com', // Thay your-domain.com bằng domain/IP của bạn
```

### 4.3. Tạo thư mục logs (nếu chưa có)

```bash
mkdir -p /www/wwwroot/your-domain.com/logs
```

### 4.4. Khởi động ứng dụng với PM2

```bash
cd /www/wwwroot/your-domain.com
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # Chạy lệnh này và làm theo hướng dẫn để tự động khởi động khi server reboot
```

### 4.5. Kiểm tra trạng thái

```bash
pm2 status
pm2 logs ocr-server
```

Bạn sẽ thấy log của ứng dụng. Nếu có lỗi, kiểm tra và sửa.

## Bước 5: Cấu hình Nginx

### 5.1. Cấu hình Nginx trong aaPanel

1. Vào **Website** → Click vào domain của bạn
2. Chọn **Settings** → **Configuration**
3. Xóa nội dung cũ và paste cấu hình sau:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Thay đổi domain của bạn
    
    # Logs
    access_log /www/wwwlogs/your-domain.com.log;
    error_log /www/wwwlogs/your-domain.com.error.log;
    
    # Upload size limit (tăng nếu cần xử lý ảnh lớn)
    client_max_body_size 10M;
    
    # Timeout settings (tăng cho OCR xử lý lâu)
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    
    # Main location - proxy to FastAPI
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
    }
    
    # Health check endpoint (tùy chọn)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # Static files (nếu có)
    location /static {
        alias /www/wwwroot/your-domain.com/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

**Nhớ thay `your-domain.com` bằng domain/IP thực tế của bạn!**

4. Click **Save** và **Reload** Nginx

### 5.2. Kiểm tra cấu hình Nginx

```bash
nginx -t
```

Nếu có lỗi, sửa lại. Sau đó reload:

```bash
# Trong aaPanel: Website → Settings → Reload
# Hoặc qua terminal:
systemctl reload nginx
```

## Bước 6: Cấu hình Firewall

### 6.1. Mở port trong aaPanel

1. Vào **Security** → **Firewall**
2. Thêm rule:
   - **Port**: `80` (HTTP)
   - **Port**: `443` (HTTPS - nếu dùng SSL)
   - **Port**: `8000` (chỉ mở nếu cần truy cập trực tiếp, thường không cần vì đã dùng Nginx proxy)

### 6.2. Hoặc dùng lệnh (nếu dùng ufw)

```bash
ufw allow 80/tcp
ufw allow 443/tcp
```

## Bước 7: Kiểm tra ứng dụng

### 7.1. Kiểm tra qua browser

Mở trình duyệt và truy cập:
- `http://your-domain.com/` - Xem thông tin server
- `http://your-domain.com/health` - Kiểm tra health check

### 7.2. Test API qua curl

```bash
curl http://your-domain.com/
curl http://your-domain.com/health
```

### 7.3. Test upload ảnh

```bash
curl -X POST "http://your-domain.com/ocr" \
  -F "file=@/path/to/test-image.jpg"
```

## Bước 8: Cài đặt SSL (Tùy chọn nhưng khuyến nghị)

### 8.1. Cài SSL trong aaPanel

1. Vào **Website** → Click domain → **SSL**
2. Chọn **Let's Encrypt** (miễn phí)
3. Điền email và click **Apply**
4. Bật **Force HTTPS**

### 8.2. Cập nhật Nginx config cho HTTPS

Sau khi cài SSL, cấu hình sẽ tự động thêm HTTPS. Nếu cần chỉnh sửa, thêm vào config:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /www/server/panel/vhost/cert/your-domain.com/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/your-domain.com/privkey.pem;
    
    # ... (copy các config từ server block HTTP ở trên)
}
```

## Bước 9: Tối ưu hóa và bảo mật

### 9.1. Cấu hình PM2 auto-restart

PM2 đã được cấu hình auto-restart trong `ecosystem.config.js`. Kiểm tra:

```bash
pm2 info ocr-server
```

### 9.2. Giới hạn memory (nếu cần)

Trong `ecosystem.config.js`, có thể điều chỉnh:
```javascript
max_memory_restart: '1G',  // Tăng/giảm tùy server
```

### 9.3. Tối ưu số workers

Trong file `start.sh`, có thể điều chỉnh số workers:
```bash
--workers 1  # Server nhỏ: 1 worker
--workers 2  # Server vừa: 2 workers
--workers 4  # Server lớn: 4 workers
```

### 9.4. Bảo mật

- Đảm bảo file `.env` (nếu có) không được public
- Kiểm tra quyền file: `chmod 600 .env`
- Không commit thông tin nhạy cảm lên Git

## Troubleshooting

### Lỗi: Port 8000 đã được sử dụng

```bash
# Kiểm tra process đang dùng port 8000
lsof -i :8000
# Hoặc
netstat -tulpn | grep 8000

# Kill process nếu cần
kill -9 <PID>
```

### Lỗi: PM2 không khởi động được

1. Kiểm tra log: `pm2 logs ocr-server`
2. Kiểm tra Python path trong `ecosystem.config.js`
3. Đảm bảo virtual environment đã được activate đúng cách

### Lỗi: EasyOCR không tải được model

1. Kiểm tra kết nối internet
2. Kiểm tra dung lượng ổ cứng: `df -h`
3. Thử tải model thủ công:
```bash
python3 -c "import easyocr; reader = easyocr.Reader(['vi', 'en'])"
```

### Lỗi: Nginx 502 Bad Gateway

1. Kiểm tra ứng dụng có đang chạy: `pm2 status`
2. Kiểm tra port 8000: `curl http://127.0.0.1:8000/health`
3. Kiểm tra log Nginx: `/www/wwwlogs/your-domain.com.error.log`

### Lỗi: Permission denied

```bash
# Cấp quyền cho thư mục uploads
chmod 755 /www/wwwroot/your-domain.com/uploads
chown -R www:www /www/wwwroot/your-domain.com/uploads
```

## Quản lý ứng dụng

### Xem logs

```bash
# PM2 logs
pm2 logs ocr-server

# Nginx logs
tail -f /www/wwwlogs/your-domain.com.log
tail -f /www/wwwlogs/your-domain.com.error.log
```

### Restart ứng dụng

```bash
pm2 restart ocr-server
```

### Stop/Start ứng dụng

```bash
pm2 stop ocr-server
pm2 start ocr-server
```

### Xem thông tin ứng dụng

```bash
pm2 info ocr-server
pm2 monit
```

## Cập nhật code mới

1. Backup code hiện tại (khuyến nghị)
2. Upload code mới hoặc pull từ Git
3. Cài đặt dependencies mới (nếu có):
```bash
cd /www/wwwroot/your-domain.com
source venv/bin/activate
pip install -r requirements.txt
```
4. Restart ứng dụng:
```bash
pm2 restart ocr-server
```

## Kết luận

Sau khi hoàn thành các bước trên, ứng dụng OCR Server của bạn đã sẵn sàng chạy trên production. 

**Các endpoint chính:**
- `GET /` - Thông tin server
- `GET /health` - Health check
- `POST /ocr` - Upload ảnh và trích xuất text

**Lưu ý:**
- Lần đầu chạy có thể chậm do EasyOCR tải model
- Đảm bảo server có đủ RAM (tối thiểu 2GB, khuyến nghị 4GB+)
- Theo dõi logs thường xuyên để phát hiện lỗi sớm

