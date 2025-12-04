#!/bin/bash

# Script khởi động OCR Server
# Sử dụng với PM2 hoặc chạy trực tiếp

# Đường dẫn thư mục dự án (thay đổi theo server của bạn)
PROJECT_DIR="/www/wwwroot/your-domain.com"
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source venv/bin/activate

# Chạy server với uvicorn
# Có thể điều chỉnh số workers tùy theo server
# --workers 1: 1 worker (phù hợp server nhỏ)
# --workers 2-4: nhiều workers (server mạnh hơn)
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info

# Hoặc chạy trực tiếp với Python (nếu không dùng uvicorn)
# python -m app.main

