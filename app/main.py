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
from app.models import OCRResponse, StandardizeAddressRequest, StandardizeAddressResponse
from vietnamadminunits import convert_address

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
        
        # Convert địa chỉ từ format cũ (63 tỉnh) sang format mới (34 tỉnh)
        try:
            # Sử dụng convert_address để chuyển đổi từ format cũ sang mới
            converted_address = convert_address(request.address)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

