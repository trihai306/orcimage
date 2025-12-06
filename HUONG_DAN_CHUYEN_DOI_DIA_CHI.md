# Hướng Dẫn Chuyển Đổi Địa Chỉ Từ 63 Tỉnh Sang 34 Tỉnh (2025)

## Tổng Quan

Sau sáp nhập hành chính tháng 7/2025, Việt Nam đã giảm từ **63 tỉnh/thành phố** xuống **34 tỉnh/thành phố**. API `/standardize-address` giúp chuyển đổi địa chỉ từ format cũ sang format mới.

## API Endpoint

```
POST /standardize-address
Content-Type: application/json
```

## Format Input Hợp Lệ

### 1. Format Chuẩn (Khuyến Nghị)

**Format tốt nhất**: `"(street), ward, district, province"`

**Ví dụ:**
```
59 nguyễn sỹ sách, p15, tan binh, hcm
Đường 15, long bình, quận 9, hcm
Số 61, Phố Tây Trà, Phường Trần Phú, Quận Hoàng Mai, Thành Phố Hà Nội
```

### 2. Các Format Được Hỗ Trợ

#### Format 1: Đầy đủ (Street, Ward, District, Province)
```
"TTTM Vincom Plaza, Phường Suối Hoa, Thành Phố Bắc Ninh, Tỉnh Bắc Ninh"
"Số 61, Phố Tây Trà, Phường Trần Phú, Quận Hoàng Mai, Thành Phố Hà Nội"
```

#### Format 2: Không có Street (Ward, District, Province)
```
"Phường Suối Hoa, Thành Phố Bắc Ninh, Tỉnh Bắc Ninh"
"Xã Phượng Mao, Huyện Quế Võ, Tỉnh Bắc Ninh"
```

#### Format 3: Không có District (Ward, Province) - Chỉ áp dụng cho một số tỉnh
```
"Phường Tân Sơn, Hồ Chí Minh"
"Xã Yên Phong, Bắc Ninh"
```

#### Format 4: Có Thôn/Xóm (Street/Thôn, Ward, District, Province)
```
"Thôn Mao Dộc, Xã Phượng Mao, Huyện Quế Võ, Tỉnh Bắc Ninh"
"Xóm Giếng, Xã Hồng Tiến, Thị Xã Phổ Yên, Tỉnh Thái Nguyên"
```

### 3. Lưu Ý Quan Trọng

#### ✅ Được Hỗ Trợ:
- **Case không quan trọng**: `hcm`, `HCM`, `Hcm` đều được
- **Dấu tiếng Việt**: Thường được ignore, nhưng nên có để chính xác hơn
- **Viết tắt**: `hcm`, `hn`, `hà nội` đều được nhận diện
- **Có hoặc không có tiền tố**: `Phường`, `Xã`, `Quận`, `Huyện`, `Tỉnh`, `Thành phố`
- **Dấu phẩy hoặc không**: Có thể có hoặc không có dấu phẩy giữa các phần

#### ⚠️ Cần Chú Ý:
- **Thứ tự**: Nên theo thứ tự `(street), ward, district, province`
- **Đủ thông tin**: Cần có ít nhất `ward` và `province` để chuyển đổi chính xác
- **Tên địa danh cũ**: Phải là tên đúng theo format 63 tỉnh (trước 2025)

## Request Body

```json
{
  "address": "string (required) - Địa chỉ cần chuẩn hóa",
  "convert_mode": "CONVERT_2025 (optional, default)",
  "short_name": true (optional, default: true)
}
```

### Parameters:

- **address** (required): Địa chỉ ở format cũ (63 tỉnh)
- **convert_mode** (optional): Hiện tại chỉ hỗ trợ `"CONVERT_2025"` (mặc định)
- **short_name** (optional): 
  - `true` (mặc định): Trả về tên ngắn (ví dụ: "Bắc Ninh", "Yên Phong")
  - `false`: Trả về tên đầy đủ (ví dụ: "Tỉnh Bắc Ninh", "Xã Yên Phong")

## Response Format

```json
{
  "success": true,
  "original_address": "Địa chỉ gốc",
  "standardized_address": "Địa chỉ đã chuẩn hóa (format mới 34 tỉnh)",
  "province": "Tỉnh/Thành phố (đã chuẩn hóa)",
  "district": "Quận/Huyện (nếu có)",
  "ward": "Phường/Xã (đã chuẩn hóa)",
  "street": "Đường/Thôn/Xóm (nếu có)",
  "error": null
}
```

## Ví Dụ Sử Dụng

### Ví dụ 1: Địa chỉ đầy đủ với short_name=true

**Request:**
```json
{
  "address": "TTTM Vincom Plaza, Phường Suối Hoa, Thành Phố Bắc Ninh, Tỉnh Bắc Ninh"
}
```

**Response:**
```json
{
  "success": true,
  "original_address": "TTTM Vincom Plaza, Phường Suối Hoa, Thành Phố Bắc Ninh, Tỉnh Bắc Ninh",
  "standardized_address": "TTTM Vincom Plaza, Suối Hoa, Bắc Ninh",
  "province": "Bắc Ninh",
  "district": null,
  "ward": "Suối Hoa",
  "street": "TTTM Vincom Plaza",
  "error": null
}
```

### Ví dụ 2: Địa chỉ có thôn/xóm

**Request:**
```json
{
  "address": "Thôn Mao Dộc, Xã Phượng Mao, Huyện Quế Võ, Tỉnh Bắc Ninh"
}
```

**Response:**
```json
{
  "success": true,
  "original_address": "Thôn Mao Dộc, Xã Phượng Mao, Huyện Quế Võ, Tỉnh Bắc Ninh",
  "standardized_address": "Thôn Mao Dộc, Phượng Mao, Bắc Ninh",
  "province": "Bắc Ninh",
  "district": null,
  "ward": "Phượng Mao",
  "street": "Thôn Mao Dộc",
  "error": null
}
```

### Ví dụ 3: Địa chỉ với short_name=false (tên đầy đủ)

**Request:**
```json
{
  "address": "Số 61, Phố Tây Trà, Phường Trần Phú, Quận Hoàng Mai, Thành Phố Hà Nội",
  "short_name": false
}
```

**Response:**
```json
{
  "success": true,
  "original_address": "Số 61, Phố Tây Trà, Phường Trần Phú, Quận Hoàng Mai, Thành Phố Hà Nội",
  "standardized_address": "Số 61 Phố Tây Trà, Phường Trần Phú, Thủ đô Hà Nội",
  "province": "Thủ đô Hà Nội",
  "district": null,
  "ward": "Phường Trần Phú",
  "street": "Số 61 Phố Tây Trà",
  "error": null
}
```

## Các Trường Hợp Đặc Biệt

### 1. Địa chỉ có KCN (Khu Công Nghiệp)

**Input:**
```
"Lô CN-03 và Lô CN-12, KCN Đồng Văn IV, Xã Đại Cương, Huyện Kim Bảng, Tỉnh Hà Nam"
```

**Output:**
- KCN thường được coi là phần của `street`
- Xã, Huyện, Tỉnh sẽ được chuyển đổi sang format mới

### 2. Địa chỉ có Quốc lộ/KM

**Input:**
```
"KM số 8 Quốc lộ 18, Thôn Mao Dộc, Xã Phượng Mao, Huyện Quế Võ, Tỉnh Bắc Ninh"
```

**Output:**
- "KM số 8 Quốc lộ 18" và "Thôn Mao Dộc" có thể được gộp vào `street`
- Các đơn vị hành chính sẽ được chuyển đổi

### 3. Địa chỉ có nhiều thông tin bổ sung

**Input:**
```
"Nhà xưởng CN5, KCN Bá Thiện 1, xã Thiện Kế, Bình Xuyên, Vĩnh Phúc (nằm trong interflex)"
```

**Output:**
- Phần trong ngoặc đơn thường bị loại bỏ
- Các đơn vị hành chính sẽ được chuẩn hóa

## Cách Gọi API

### cURL

```bash
curl -X POST "https://ocr.toanthinhvn.com/standardize-address" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "TTTM Vincom Plaza, Phường Suối Hoa, Thành Phố Bắc Ninh, Tỉnh Bắc Ninh"
  }'
```

### Python

```python
import requests

url = "https://ocr.toanthinhvn.com/standardize-address"
data = {
    "address": "TTTM Vincom Plaza, Phường Suối Hoa, Thành Phố Bắc Ninh, Tỉnh Bắc Ninh",
    "short_name": True
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### JavaScript

```javascript
fetch('https://ocr.toanthinhvn.com/standardize-address', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    address: 'TTTM Vincom Plaza, Phường Suối Hoa, Thành Phố Bắc Ninh, Tỉnh Bắc Ninh',
    short_name: true
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Lưu Ý Quan Trọng

1. **Format Input**: Nên sử dụng format `"(street), ward, district, province"` để đạt độ chính xác cao nhất

2. **Thứ tự**: Thứ tự các thành phần nên đúng, nhưng thư viện có thể tự động phát hiện trong một số trường hợp

3. **Tên địa danh cũ**: Đảm bảo tên địa danh là đúng theo format 63 tỉnh (trước 2025)

4. **Một số địa danh nhỏ**: Các địa danh nhỏ như thôn, xóm có thể bị loại bỏ nếu không có trong database của thư viện

5. **short_name**: 
   - `true`: Tên ngắn gọn, dễ đọc (khuyến nghị)
   - `false`: Tên đầy đủ với tiền tố (ví dụ: "Tỉnh Bắc Ninh", "Xã Yên Phong")

## Xử Lý Lỗi

### Lỗi: Địa chỉ không được để trống
```json
{
  "success": false,
  "error": "Địa chỉ không được để trống"
}
```

### Lỗi: Không thể convert địa chỉ
```json
{
  "success": false,
  "error": "Lỗi khi convert địa chỉ: [chi tiết lỗi]"
}
```

Có thể do:
- Địa chỉ không đúng format
- Tên địa danh không tồn tại trong database
- Thiếu thông tin cần thiết (ward, province)

