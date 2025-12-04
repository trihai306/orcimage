import easyocr
import os
from typing import Optional, Tuple


class OCRService:
    def __init__(self):
        """Khởi tạo EasyOCR reader với tiếng Việt và tiếng Anh"""
        print("Đang khởi tạo EasyOCR reader...")
        self.reader = easyocr.Reader(['vi', 'en'], gpu=False)
        print("EasyOCR reader đã sẵn sàng!")
    
    def extract_text(self, image_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Trích xuất text từ ảnh
        
        Args:
            image_path: Đường dẫn đến file ảnh
            
        Returns:
            Tuple (success, text, error_message)
        """
        try:
            if not os.path.exists(image_path):
                return False, "", f"File không tồn tại: {image_path}"
            
            # Đọc text từ ảnh
            results = self.reader.readtext(image_path)
            
            # Kết hợp tất cả text đã đọc được
            extracted_text = "\n".join([result[1] for result in results])
            
            if not extracted_text.strip():
                return False, "", "Không tìm thấy text trong ảnh"
            
            return True, extracted_text, None
            
        except Exception as e:
            error_msg = f"Lỗi khi xử lý OCR: {str(e)}"
            return False, "", error_msg

