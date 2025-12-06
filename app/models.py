from pydantic import BaseModel
from typing import Optional, List, Dict, Any


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


class LookupAdminUnitRequest(BaseModel):
    """
    Request model cho API tra cứu đơn vị hành chính
    Cho phép truyền các tham số riêng lẻ để tìm thông tin chuẩn
    """
    province: Optional[str] = None  # Tỉnh/Thành phố (format cũ 63 tỉnh)
    district: Optional[str] = None  # Quận/Huyện/Thị xã (format cũ 63 tỉnh)
    ward: Optional[str] = None  # Phường/Xã/Thị trấn (format cũ 63 tỉnh)
    short_name: Optional[bool] = True  # Sử dụng tên ngắn hay đầy đủ


class AdminUnitInfo(BaseModel):
    """Thông tin đơn vị hành chính"""
    province: Optional[str] = None
    province_full: Optional[str] = None
    province_code: Optional[str] = None
    district: Optional[str] = None
    district_full: Optional[str] = None
    district_code: Optional[str] = None
    ward: Optional[str] = None
    ward_full: Optional[str] = None
    ward_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LookupAdminUnitResponse(BaseModel):
    """Response model cho API tra cứu đơn vị hành chính"""
    success: bool
    original: Dict[str, Optional[str]]  # Thông tin gốc đã truyền vào
    standardized: Optional[AdminUnitInfo] = None  # Thông tin đã chuẩn hóa (format mới 34 tỉnh)
    error: Optional[str] = None

