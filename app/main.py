import sys
import os
from pathlib import Path

# Đảm bảo PYTHONPATH đúng khi chạy từ aaPanel
PROJECT_DIR = Path(__file__).parent.parent.absolute()
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
os.chdir(PROJECT_DIR)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uuid

from app.ocr_service import OCRService
from app.models import (
    OCRResponse, 
    StandardizeAddressRequest, 
    StandardizeAddressResponse,
    LookupAdminUnitRequest,
    LookupAdminUnitResponse,
    AdminUnitInfo
)
from vietnamadminunits import convert_address, parse_address, ParseMode

app = FastAPI(
    title="OCR ID Card Server",
    description="Server OCR đọc text từ ảnh căn cước",
    version="1.0.0"
)

# OCR service sẽ được khởi tạo lazy
ocr_service = None

# Tạo thư mục uploads nếu chưa có
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Định nghĩa các định dạng ảnh được hỗ trợ
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


@app.get("/")
async def root():
    """Endpoint kiểm tra server"""
    return {
        "message": "OCR ID Card Server đang chạy",
        "endpoints": {
            "ocr": "/ocr (POST) - Upload ảnh để trích xuất text",
            "standardize_address": "/standardize-address (POST) - Chuẩn hóa địa chỉ từ format cũ (63 tỉnh) sang format mới (34 tỉnh)",
            "lookup_admin_unit": "/lookup-admin-unit (POST) - Tra cứu đơn vị hành chính theo từng cấp độ (xã, quận, huyện, tỉnh)",
            "health": "/health (GET) - Kiểm tra trạng thái server"
        }
    }


@app.get("/health")
async def health():
    """Kiểm tra trạng thái server"""
    global ocr_service
    ocr_status = "ready" if ocr_service is not None else "initializing"
    return {
        "status": "healthy", 
        "service": "OCR ID Card Server",
        "ocr_status": ocr_status
    }


def get_ocr_service():
    """Lazy initialization của OCR service"""
    global ocr_service
    if ocr_service is None:
        ocr_service = OCRService()
    return ocr_service


@app.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    Endpoint nhận ảnh và trích xuất text
    
    Args:
        file: File ảnh upload qua form-data
        
    Returns:
        OCRResponse với text đã trích xuất
    """
    # Kiểm tra định dạng file
    file_extension = Path(file.filename).suffix
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Tạo tên file unique để lưu tạm
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Lưu file tạm
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Trích xuất text
        ocr = get_ocr_service()
        success, text, error = ocr.extract_text(str(temp_file_path))
        
        if success:
            return OCRResponse(
                success=True,
                text=text,
                language="vi"
            )
        else:
            return OCRResponse(
                success=False,
                text="",
                language="vi",
                error=error
            )
    
    except Exception as e:
        return OCRResponse(
            success=False,
            text="",
            language="vi",
            error=f"Lỗi server: {str(e)}"
        )
    
    finally:
        # Xóa file tạm sau khi xử lý
        if temp_file_path.exists():
            os.remove(temp_file_path)


@app.post("/standardize-address", response_model=StandardizeAddressResponse)
async def standardize_address_endpoint(request: StandardizeAddressRequest):
    """
    Endpoint chuẩn hóa địa chỉ Việt Nam từ format cũ (63 tỉnh) sang format mới (34 tỉnh)
    
    Sau khi sáp nhập hành chính tháng 7/2025, Việt Nam đã giảm từ 63 tỉnh/thành phố xuống 34.
    API này giúp chuyển đổi địa chỉ từ format cũ sang format mới.
    
    Args:
        request: StandardizeAddressRequest chứa:
            - address: Địa chỉ cần chuẩn hóa (format: "số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố")
            - convert_mode: Chế độ convert (mặc định: "CONVERT_2025")
            - short_name: Sử dụng tên ngắn hay đầy đủ (mặc định: True)
        
    Returns:
        StandardizeAddressResponse với địa chỉ đã được chuẩn hóa
    """
    try:
        if not request.address or not request.address.strip():
            return StandardizeAddressResponse(
                success=False,
                original_address=request.address,
                standardized_address=None,
                province=None,
                district=None,
                ward=None,
                street=None,
                error="Địa chỉ không được để trống"
            )
        
        # Lưu địa chỉ gốc để giữ lại street nếu cần
        original_address_str = request.address.strip()
        
        # Convert địa chỉ từ format cũ (63 tỉnh) sang format mới (34 tỉnh)
        try:
            # Sử dụng convert_address để chuyển đổi từ format cũ sang mới
            converted_address = convert_address(original_address_str)
        except Exception as e:
            return StandardizeAddressResponse(
                success=False,
                original_address=request.address,
                standardized_address=None,
                province=None,
                district=None,
                ward=None,
                street=None,
                error=f"Lỗi khi convert địa chỉ: {str(e)}"
            )
        
        # Extract các thành phần
        province = getattr(converted_address, 'province', None)
        district = getattr(converted_address, 'district', None)
        ward = getattr(converted_address, 'ward', None)
        street = getattr(converted_address, 'street', None)
        
        # Sử dụng short_name nếu được yêu cầu
        if request.short_name:
            province = getattr(converted_address, 'short_province', province)
            district = getattr(converted_address, 'short_district', district) if district else None
            ward = getattr(converted_address, 'short_ward', ward)
        
        # Nếu street bị mất hoặc rỗng, cố gắng extract từ original_address
        # bằng cách loại bỏ các phần ward, district, province đã được nhận diện
        if not street or not street.strip():
            # Tách địa chỉ gốc thành các phần bằng dấu phẩy
            original_parts = [p.strip() for p in original_address_str.split(',')]
            
            # Tạo danh sách các từ khóa cần loại bỏ (ward, district, province)
            keywords_to_remove = []
            if ward:
                # Thêm ward và các biến thể (cả tên ngắn và đầy đủ)
                ward_short = getattr(converted_address, 'short_ward', ward)
                ward_full = getattr(converted_address, 'ward', ward)
                ward_variants = [
                    ward_short, ward_full,
                    ward_short.replace('Phường ', '').replace('Xã ', '').replace('Thị trấn ', ''),
                    ward_full.replace('Phường ', '').replace('Xã ', '').replace('Thị trấn ', ''),
                    f'Phường {ward_short}',
                    f'Xã {ward_short}',
                    f'Thị trấn {ward_short}',
                    f'Phường {ward_full}',
                    f'Xã {ward_full}',
                    f'Thị trấn {ward_full}'
                ]
                keywords_to_remove.extend([v for v in ward_variants if v])
            if district:
                district_short = getattr(converted_address, 'short_district', district) if district else None
                district_full = district
                district_variants = [
                    district_short, district_full,
                    district_short.replace('Quận ', '').replace('Huyện ', '').replace('Thị xã ', '').replace('Thành phố ', '') if district_short else None,
                    district_full.replace('Quận ', '').replace('Huyện ', '').replace('Thị xã ', '').replace('Thành phố ', ''),
                    f'Quận {district_short}' if district_short else None,
                    f'Huyện {district_short}' if district_short else None,
                    f'Thị xã {district_short}' if district_short else None,
                    f'Thành phố {district_short}' if district_short else None,
                    f'Quận {district_full}',
                    f'Huyện {district_full}',
                    f'Thị xã {district_full}',
                    f'Thành phố {district_full}'
                ]
                keywords_to_remove.extend([v for v in district_variants if v])
            if province:
                province_short = getattr(converted_address, 'short_province', province)
                province_full = getattr(converted_address, 'province', province)
                province_variants = [
                    province_short, province_full,
                    province_short.replace('Tỉnh ', '').replace('Thành phố ', '').replace('Thủ đô ', ''),
                    province_full.replace('Tỉnh ', '').replace('Thành phố ', '').replace('Thủ đô ', ''),
                    f'Tỉnh {province_short}',
                    f'Thành phố {province_short}',
                    f'Thủ đô {province_short}',
                    f'Tỉnh {province_full}',
                    f'Thành phố {province_full}',
                    f'Thủ đô {province_full}'
                ]
                keywords_to_remove.extend([v for v in province_variants if v])
            
            # Loại bỏ các phần đã được nhận diện, giữ lại phần còn lại làm street
            remaining_parts = []
            for part in original_parts:
                part_lower = part.lower().strip()
                should_remove = False
                for keyword in keywords_to_remove:
                    if keyword:
                        keyword_lower = keyword.lower().strip()
                        # Kiểm tra nếu phần này khớp với keyword (chính xác hoặc chứa)
                        if keyword_lower == part_lower or part_lower in keyword_lower or keyword_lower in part_lower:
                            # Kiểm tra thêm: nếu là province và part có chứa từ khóa tỉnh/thành phố
                            if province and ('tỉnh' in part_lower or 'thành phố' in part_lower or 'thủ đô' in part_lower):
                                if province_short.lower() in part_lower or province_full.lower() in part_lower:
                                    should_remove = True
                                    break
                            else:
                                should_remove = True
                                break
                if not should_remove:
                    remaining_parts.append(part)
            
            if remaining_parts:
                street = ', '.join(remaining_parts)
        
        # Tạo địa chỉ chuẩn hóa đẹp
        address_parts = []
        if street:
            address_parts.append(street)
        if ward:
            address_parts.append(ward)
        if district:
            address_parts.append(district)
        if province:
            address_parts.append(province)
        
        standardized_address_str = ", ".join(address_parts) if address_parts else None
        
        return StandardizeAddressResponse(
            success=True,
            original_address=request.address,
            standardized_address=standardized_address_str,
            province=province,
            district=district,
            ward=ward,
            street=street
        )
    
    except Exception as e:
        return StandardizeAddressResponse(
            success=False,
            original_address=request.address if request else "",
            standardized_address=None,
            province=None,
            district=None,
            ward=None,
            street=None,
            error=f"Lỗi server: {str(e)}"
        )


@app.post("/lookup-admin-unit", response_model=LookupAdminUnitResponse)
async def lookup_admin_unit_endpoint(request: LookupAdminUnitRequest):
    """
    Endpoint tra cứu đơn vị hành chính theo từng cấp độ
    
    Cho phép truyền các tham số riêng lẻ (province, district, ward) ở format cũ (63 tỉnh)
    và trả về thông tin chuẩn ở format mới (34 tỉnh).
    
    Ví dụ:
    - Chỉ truyền ward và district cũ → trả về thông tin mới
    - Truyền đầy đủ province, district, ward cũ → trả về thông tin mới
    
    Args:
        request: LookupAdminUnitRequest chứa:
            - province: Tỉnh/Thành phố (format cũ 63 tỉnh, optional)
            - district: Quận/Huyện/Thị xã (format cũ 63 tỉnh, optional)
            - ward: Phường/Xã/Thị trấn (format cũ 63 tỉnh, optional)
            - short_name: Sử dụng tên ngắn hay đầy đủ (mặc định: True)
        
    Returns:
        LookupAdminUnitResponse với thông tin đã được chuẩn hóa
    """
    try:
        # Kiểm tra ít nhất phải có 1 tham số
        if not request.province and not request.district and not request.ward:
            return LookupAdminUnitResponse(
                success=False,
                original={"province": request.province, "district": request.district, "ward": request.ward},
                standardized=None,
                error="Phải truyền ít nhất một trong các tham số: province, district, ward"
            )
        
        # Tạo địa chỉ từ các tham số để convert
        address_parts = []
        if request.ward:
            address_parts.append(request.ward)
        if request.district:
            address_parts.append(request.district)
        if request.province:
            address_parts.append(request.province)
        
        address_str = ", ".join(address_parts)
        
        # Sử dụng convert_address để chuyển đổi từ format cũ (63 tỉnh) sang format mới (34 tỉnh)
        try:
            converted_address = convert_address(address_str)
        except Exception as e:
            return LookupAdminUnitResponse(
                success=False,
                original={"province": request.province, "district": request.district, "ward": request.ward},
                standardized=None,
                error=f"Lỗi khi convert địa chỉ: {str(e)}"
            )
        
        # Extract các thành phần
        province_full = getattr(converted_address, 'province', None)
        district_full = getattr(converted_address, 'district', None)
        ward_full = getattr(converted_address, 'ward', None)
        
        province_code = getattr(converted_address, 'province_code', None)
        district_code = getattr(converted_address, 'district_code', None)
        ward_code = getattr(converted_address, 'ward_code', None)
        
        latitude = getattr(converted_address, 'latitude', None)
        longitude = getattr(converted_address, 'longitude', None)
        
        # Sử dụng short_name nếu được yêu cầu
        if request.short_name:
            province = getattr(converted_address, 'short_province', province_full)
            district = getattr(converted_address, 'short_district', district_full) if district_full else None
            ward = getattr(converted_address, 'short_ward', ward_full)
        else:
            province = province_full
            district = district_full
            ward = ward_full
        
        # Tạo response
        standardized_info = AdminUnitInfo(
            province=province,
            province_full=province_full,
            province_code=str(province_code) if province_code else None,
            district=district,
            district_full=district_full,
            district_code=str(district_code) if district_code else None,
            ward=ward,
            ward_full=ward_full,
            ward_code=str(ward_code) if ward_code else None,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )
        
        return LookupAdminUnitResponse(
            success=True,
            original={"province": request.province, "district": request.district, "ward": request.ward},
            standardized=standardized_info,
            error=None
        )
    
    except Exception as e:
        return LookupAdminUnitResponse(
            success=False,
            original={"province": request.province if request else None, "district": request.district if request else None, "ward": request.ward if request else None},
            standardized=None,
            error=f"Lỗi server: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

