from pydantic import BaseModel
from typing import Optional


class OCRResponse(BaseModel):
    success: bool
    text: str
    language: Optional[str] = "vi"
    error: Optional[str] = None


class StandardizeAddressRequest(BaseModel):
    """Request model cho API chuẩn hóa địa chỉ"""
    address: str
    convert_mode: Optional[str] = "CONVERT_2025"  # Chế độ convert: CONVERT_2025
    short_name: Optional[bool] = True  # Sử dụng tên ngắn hay đầy đủ


class StandardizeAddressResponse(BaseModel):
    """Response model cho API chuẩn hóa địa chỉ"""
    success: bool
    original_address: str
    standardized_address: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    street: Optional[str] = None
    error: Optional[str] = None

