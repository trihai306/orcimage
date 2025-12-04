# Hướng dẫn Deploy Nhanh lên aaPanel

## Các bước cơ bản (5 phút)

### 1. Upload code lên server

```bash
# SSH vào server
ssh root@your-server-ip

# Vào thư mục website (tạo website trong aaPanel trước)
cd /www/wwwroot/your-domain.com

# Upload code vào đây (qua File Manager hoặc Git)
```

### 2. Cài đặt Python và dependencies

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Sửa đường dẫn trong file config

```bash
# Sửa ecosystem.config.js
nano ecosystem.config.js
# Thay đổi: cwd: '/www/wwwroot/your-domain.com' → đường dẫn thực tế

# Sửa start.sh
nano start.sh
# Thay đổi: PROJECT_DIR="/www/wwwroot/your-domain.com" → đường dẫn thực tế
```

### 4. Chạy với PM2

```bash
# Cài PM2 (nếu chưa có)
npm install -g pm2

# Start app
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 5. Cấu hình Nginx trong aaPanel

1. Vào **Website** → Chọn website → **Settings** → **Configuration**
2. Copy nội dung từ `nginx.conf.example` và paste vào
3. Sửa `your-domain.com` thành domain của bạn
4. Click **Save** và **Reload**

### 6. Test

```bash
# Test local
curl http://localhost:8000/health

# Test qua domain
curl http://your-domain.com/health
```

## Checklist

- [ ] Code đã upload lên server
- [ ] Python 3.8+ đã cài đặt
- [ ] Virtual environment đã tạo và cài dependencies
- [ ] PM2 đã cài và app đang chạy
- [ ] Nginx đã cấu hình reverse proxy
- [ ] Port 8000 đã mở trong firewall
- [ ] Test API thành công

## Lệnh hữu ích

```bash
# Xem status PM2
pm2 status

# Xem logs
pm2 logs ocr-server

# Restart
pm2 restart ocr-server

# Reload Nginx
nginx -s reload
```

## Gặp vấn đề?

Xem file `DEPLOY_AAPANEL.md` để có hướng dẫn chi tiết và troubleshooting.

