# OCR ID Card Server

Server FastAPI để đọc text từ ảnh căn cước sử dụng EasyOCR.

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip

## Cài đặt

1. Clone hoặc tải dự án về

2. Tạo virtual environment (khuyến nghị):
```bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

**Lưu ý:** Lần đầu chạy, EasyOCR sẽ tự động tải các model cần thiết (có thể mất vài phút).

## Chạy server

```bash
python -m app.main
```

Hoặc sử dụng uvicorn trực tiếp:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server sẽ chạy tại: `http://localhost:8000`

## Sử dụng API

### 1. Kiểm tra server

```bash
curl http://localhost:8000/
```

### 2. Trích xuất text từ ảnh

**Sử dụng curl:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@/đường/dẫn/đến/ảnh.jpg"
```

**Sử dụng Python requests:**
```python
import requests

url = "http://localhost:8000/ocr"
files = {"file": open("path/to/image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Sử dụng Postman:**
1. Chọn method: POST
2. URL: `http://localhost:8000/ocr`
3. Body → form-data
4. Key: `file` (type: File)
5. Chọn file ảnh và gửi request

### 3. Response mẫu

**Thành công:**
```json
{
  "success": true,
  "text": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n...",
  "language": "vi"
}
```

**Lỗi:**
```json
{
  "success": false,
  "text": "",
  "language": "vi",
  "error": "Không tìm thấy text trong ảnh"
}
```

## API Endpoints

- `GET /` - Thông tin server và danh sách endpoints
- `GET /health` - Kiểm tra trạng thái server
- `POST /ocr` - Trích xuất text từ ảnh căn cước

## Định dạng ảnh hỗ trợ

- JPG/JPEG
- PNG

## Lưu ý

- Ảnh upload sẽ được lưu tạm trong thư mục `uploads/` và tự động xóa sau khi xử lý
- EasyOCR hỗ trợ tiếng Việt và tiếng Anh
- Lần đầu chạy có thể mất thời gian để tải model
- Để tăng tốc độ xử lý, có thể sử dụng GPU bằng cách cài đặt PyTorch với CUDA

## Deploy lên Production

### Deploy lên aaPanel

Xem hướng dẫn chi tiết:
- **[DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md)** - Hướng dẫn deploy nhanh (5 phút)
- **[DEPLOY_AAPANEL.md](DEPLOY_AAPANEL.md)** - Hướng dẫn chi tiết đầy đủ

### Files hỗ trợ deploy

- `ecosystem.config.js` - Cấu hình PM2
- `start.sh` - Script khởi động server
- `nginx.conf.example` - Cấu hình Nginx mẫu

## Troubleshooting

**Lỗi khi cài đặt EasyOCR:**
- Đảm bảo đã cài đặt đầy đủ dependencies: `pip install -r requirements.txt`
- Trên macOS, có thể cần cài thêm: `brew install libmagic`

**Lỗi khi chạy server:**
- Kiểm tra port 8000 có đang được sử dụng không
- Đảm bảo đã activate virtual environment

