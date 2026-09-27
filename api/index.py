import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler
import yt_dlp
import cv2

def get_video_frames(video_url, resolution=32, max_frames=8):
    # Cấu hình yt-dlp để lấy định dạng thấp nhất (nhanh nhất)
    ydl_opts = {
        'format': 'worst[ext=mp4]', 
        'quiet': True,
        'noplaylist': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info['url']
    except Exception as e:
        return {"error": f"Lỗi lấy link video: {str(e)}"}

    # Mở luồng video bằng OpenCV
    cap = cv2.VideoCapture(stream_url)
    frames_data = []
    count = 0
    
    while cap.isOpened() and count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize khung hình về kích thước (ví dụ: 32x32)
        frame_resized = cv2.resize(frame, (resolution, resolution))
        # Chuyển đổi hệ màu từ BGR (OpenCV) sang RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        pixel_data = []
        for y in range(resolution):
            for x in range(resolution):
                r, g, b = frame_rgb[y, x]
                pixel_data.append({
                    "x": x + 1,
                    "y": y + 1,
                    "r": int(r),
                    "g": int(g),
                    "b": int(b)
                })
        
        frames_data.append(pixel_data)
        count += 1
        
        # Nhảy cóc khung hình (Skip frames) để video chạy giống stop-motion
        # Bỏ qua 15 khung hình tiếp theo (~0.5 giây của video)
        for _ in range(15): 
            cap.read()
            
    cap.release()
    return frames_data

# Hàm Handler mặc định của Vercel
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        
        url = query.get('url', [''])[0]
        res = int(query.get('res', ['32'])[0])
        
        # Cấu hình Header trả về JSON và cho phép Roblox truy cập (CORS)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not url:
            error_msg = json.dumps({"error": "Vui lòng cung cấp url. Ví dụ: ?url=LINK&res=32"})
            self.wfile.write(error_msg.encode('utf-8'))
            return
            
        # Lấy dữ liệu và trả về JSON
        data = get_video_frames(url, res)
        self.wfile.write(json.dumps(data).encode('utf-8'))
