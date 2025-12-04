#!/usr/bin/env python3
"""
Wrapper script để chạy ứng dụng OCR Server
Script này đảm bảo chạy từ đúng thư mục và dùng đúng Python path
"""
import sys
import os
from pathlib import Path

# Lấy đường dẫn thư mục dự án (thư mục chứa file này)
PROJECT_DIR = Path(__file__).parent.absolute()
os.chdir(PROJECT_DIR)

# Thêm thư mục dự án vào PYTHONPATH
sys.path.insert(0, str(PROJECT_DIR))

# Import và chạy ứng dụng
if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

