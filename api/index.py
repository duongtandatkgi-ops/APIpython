from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

# Khởi tạo API
app = FastAPI(
    title="Python API on Vercel",
    description="API Python Serverless chạy trên Vercel",
    version="1.0.0",
)


# Cấu trúc dữ liệu gửi lên API (dạng JSON)
class DataModel(BaseModel):
  message: str
  user_id: Optional[str] = "Anonymous"


# Route 1: Trang chủ / Kiểm tra API
@app.get("/")
def home():
  return {
      "status": "online",
      "message": "API Python trên Vercel đang chạy tốt!",
      "endpoints": ["/api/info", "/api/process"],
  }


# Route 2: Lấy thông tin (Phương thức GET)
@app.get("/api/info")
def get_info():
  return {
      "author": "Your Name",
      "server": "Vercel Serverless Python",
      "features": ["FastAPI", "JSON Response", "Auto Deploy"],
  }


# Route 3: Xử lý dữ liệu từ ứng dụng gửi tới (Phương thức POST)
@app.post("/api/process")
def process_data(data: DataModel):
  text_received = data.message
  sender = data.user_id

  # Viết logic xử lý dữ liệu của bạn tại đây
  reply_text = (
      f"Chào {sender}! API đã nhận và xử lý xong nội dung: '{text_received}'"
  )

  return {
      "success": True,
      "received": text_received,
      "sender": sender,
      "api_response": reply_text,
  }
