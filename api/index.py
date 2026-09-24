from fastapi import FastAPI
import requests

app = FastAPI()


@app.get("/")
def home():
  return {"status": "API Proxy đang chạy!"}


# API nhận từ khóa và gọi web/Google giả lập hoặc tìm kiếm
@app.get("/api/search")
def search_google(query: str):
  try:
    # Ví dụ dùng API công khai hoặc cào dữ liệu nhẹ từ một nguồn mở qua Python
    # Ở đây dùng một public API dạng JSON tương đương để Roblox dễ đọc
    res = requests.get(
        f"https://api.duckduckgo.com/?q={query}&format=json", timeout=5
    )
    data = res.json()

    # Lấy câu trả lời tóm tắt nếu có
    abstract = data.get("AbstractText", "")
    if not abstract:
      abstract = (
          "Không tìm thấy kết quả tóm tắt trực tiếp, nhưng API đã nhận từ khóa."
      )

    return {"success": True, "query": query, "result": abstract}
  except Exception as e:
    return {"success": False, "error": str(e)}


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
