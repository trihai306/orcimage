# Hướng Dẫn API Tra Cứu Đơn Vị Hành Chính

## Tổng Quan

API `/lookup-admin-unit` cho phép tra cứu đơn vị hành chính theo từng cấp độ (xã, quận, huyện, tỉnh/thành phố). Bạn có thể truyền các tham số riêng lẻ ở format cũ (63 tỉnh) và nhận thông tin chuẩn ở format mới (34 tỉnh).

## API Endpoint

```
POST /lookup-admin-unit
Content-Type: application/json
```

## Request Body

```json
{
  "province": "string (optional) - Tỉnh/Thành phố (format cũ 63 tỉnh)",
  "district": "string (optional) - Quận/Huyện/Thị xã (format cũ 63 tỉnh)",
  "ward": "string (optional) - Phường/Xã/Thị trấn (format cũ 63 tỉnh)",
  "short_name": true (optional, default: true) - Sử dụng tên ngắn hay đầy đủ
}
```

### Parameters:

- **province** (optional): Tỉnh/Thành phố ở format cũ (63 tỉnh)
  - Ví dụ: "Tỉnh Bắc Ninh", "Thành phố Hà Nội", "Bắc Ninh", "Hà Nội"
  
- **district** (optional): Quận/Huyện/Thị xã ở format cũ (63 tỉnh)
  - Ví dụ: "Huyện Yên Phong", "Quận Hoàng Mai", "Yên Phong", "Hoàng Mai"
  
- **ward** (optional): Phường/Xã/Thị trấn ở format cũ (63 tỉnh)
  - Ví dụ: "Xã Đông Tiến", "Phường Suối Hoa", "Đông Tiến", "Suối Hoa"
  
- **short_name** (optional): 
  - `true` (mặc định): Trả về tên ngắn (ví dụ: "Bắc Ninh", "Yên Phong")
  - `false`: Trả về tên đầy đủ (ví dụ: "Tỉnh Bắc Ninh", "Xã Yên Phong")

### Lưu Ý:

- Phải truyền ít nhất một trong các tham số: `province`, `district`, hoặc `ward`
- Có thể truyền riêng lẻ hoặc kết hợp các tham số
- Tên có thể có hoặc không có tiền tố (ví dụ: "Bắc Ninh" hoặc "Tỉnh Bắc Ninh" đều được)

## Response Format

```json
{
  "success": true,
  "original": {
    "province": "Tỉnh Bắc Ninh",
    "district": "Huyện Yên Phong",
    "ward": "Xã Đông Tiến"
  },
  "standardized": {
    "province": "Bắc Ninh",
    "province_full": "Tỉnh Bắc Ninh",
    "province_code": "27",
    "district": null,
    "district_full": null,
    "district_code": null,
    "ward": "Yên Phong",
    "ward_full": "Xã Yên Phong",
    "ward_code": "27007",
    "latitude": 21.1234,
    "longitude": 105.5678
  },
  "error": null
}
```

### Response Fields:

- **success**: Trạng thái thành công/thất bại
- **original**: Thông tin gốc đã truyền vào
- **standardized**: Thông tin đã chuẩn hóa (format mới 34 tỉnh)
  - **province**: Tên tỉnh ngắn (nếu short_name=true)
  - **province_full**: Tên tỉnh đầy đủ
  - **province_code**: Mã tỉnh
  - **district**: Tên quận/huyện ngắn (nếu có)
  - **district_full**: Tên quận/huyện đầy đủ (nếu có)
  - **district_code**: Mã quận/huyện (nếu có)
  - **ward**: Tên phường/xã ngắn (nếu có)
  - **ward_full**: Tên phường/xã đầy đủ (nếu có)
  - **ward_code**: Mã phường/xã (nếu có)
  - **latitude**: Vĩ độ (nếu có)
  - **longitude**: Kinh độ (nếu có)
- **error**: Thông báo lỗi nếu có

## Ví Dụ Sử Dụng

### Ví dụ 1: Chỉ truyền ward và district cũ

**Request:**
```json
{
  "ward": "Xã Đông Tiến",
  "district": "Huyện Yên Phong",
  "short_name": true
}
```

**Response:**
```json
{
  "success": true,
  "original": {
    "province": null,
    "district": "Huyện Yên Phong",
    "ward": "Xã Đông Tiến"
  },
  "standardized": {
    "province": "Bắc Ninh",
    "province_full": "Tỉnh Bắc Ninh",
    "province_code": "27",
    "district": null,
    "ward": "Yên Phong",
    "ward_full": "Xã Yên Phong",
    "ward_code": "27007"
  }
}
```

### Ví dụ 2: Chỉ truyền province cũ

**Request:**
```json
{
  "province": "Tỉnh Hà Nam",
  "short_name": true
}
```

**Response:**
```json
{
  "success": true,
  "original": {
    "province": "Tỉnh Hà Nam",
    "district": null,
    "ward": null
  },
  "standardized": {
    "province": "Ninh Bình",
    "province_full": "Tỉnh Ninh Bình",
    "province_code": "37"
  }
}
```

### Ví dụ 3: Truyền đầy đủ province, district, ward cũ

**Request:**
```json
{
  "province": "Tỉnh Vĩnh Phúc",
  "district": "Huyện Bình Xuyên",
  "ward": "Xã Bá Hiến",
  "short_name": false
}
```

**Response:**
```json
{
  "success": true,
  "original": {
    "province": "Tỉnh Vĩnh Phúc",
    "district": "Huyện Bình Xuyên",
    "ward": "Xã Bá Hiến"
  },
  "standardized": {
    "province": "Phú Thọ",
    "province_full": "Tỉnh Phú Thọ",
    "province_code": "25",
    "district": null,
    "ward": "Bình Tuyền",
    "ward_full": "Xã Bình Tuyền",
    "ward_code": "25001"
  }
}
```

### Ví dụ 4: Chỉ truyền district cũ

**Request:**
```json
{
  "district": "Quận Hoàng Mai",
  "short_name": true
}
```

**Response:**
```json
{
  "success": true,
  "original": {
    "province": null,
    "district": "Quận Hoàng Mai",
    "ward": null
  },
  "standardized": {
    "province": "Hà Nội",
    "province_full": "Thủ đô Hà Nội",
    "province_code": "01",
    "district": null,
    "ward": null
  }
}
```

## Cách Gọi API

### cURL

```bash
curl -X POST "http://localhost:8000/lookup-admin-unit" \
  -H "Content-Type: application/json" \
  -d '{
    "ward": "Xã Đông Tiến",
    "district": "Huyện Yên Phong"
  }'
```

### Python

```python
import requests

url = "http://localhost:8000/lookup-admin-unit"
data = {
    "ward": "Xã Đông Tiến",
    "district": "Huyện Yên Phong",
    "short_name": True
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### JavaScript

```javascript
fetch('http://localhost:8000/lookup-admin-unit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    ward: 'Xã Đông Tiến',
    district: 'Huyện Yên Phong',
    short_name: true
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Xử Lý Lỗi

### Lỗi: Không truyền tham số nào

```json
{
  "success": false,
  "original": {
    "province": null,
    "district": null,
    "ward": null
  },
  "standardized": null,
  "error": "Phải truyền ít nhất một trong các tham số: province, district, ward"
}
```

### Lỗi: Không tìm thấy đơn vị hành chính

```json
{
  "success": false,
  "original": {
    "province": "Tỉnh Không Tồn Tại",
    "district": null,
    "ward": null
  },
  "standardized": null,
  "error": "Lỗi khi convert địa chỉ: [chi tiết lỗi]"
}
```

## So Sánh Với API `/standardize-address`

| Tính năng | `/standardize-address` | `/lookup-admin-unit` |
|-----------|------------------------|---------------------|
| Input | Địa chỉ đầy đủ (string) | Các tham số riêng lẻ (province, district, ward) |
| Use case | Chuyển đổi địa chỉ hoàn chỉnh | Tra cứu từng cấp độ đơn vị hành chính |
| Output | Địa chỉ chuẩn hóa + các thành phần | Thông tin chi tiết (code, lat/lng) |
| Flexibility | Cần địa chỉ đầy đủ | Linh hoạt, chỉ cần 1 tham số |

## Lưu Ý Quan Trọng

1. **Format Input**: Tên có thể có hoặc không có tiền tố (ví dụ: "Bắc Ninh" hoặc "Tỉnh Bắc Ninh" đều được)

2. **Sáp nhập hành chính**: Một số tỉnh/huyện/xã cũ đã được sáp nhập vào đơn vị mới:
   - Ví dụ: "Tỉnh Hà Nam" → "Tỉnh Ninh Bình"
   - Ví dụ: "Huyện Bình Xuyên, Tỉnh Vĩnh Phúc" → "Tỉnh Phú Thọ"

3. **District trong format mới**: Một số quận/huyện cũ đã bị loại bỏ trong format mới (34 tỉnh), nên `district` có thể là `null`

4. **short_name**: 
   - `true`: Tên ngắn gọn, dễ đọc (khuyến nghị)
   - `false`: Tên đầy đủ với tiền tố (ví dụ: "Tỉnh Bắc Ninh", "Xã Yên Phong")

