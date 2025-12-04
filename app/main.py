from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from pathlib import Path

from app.ocr_service import OCRService
from app.models import OCRResponse

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

