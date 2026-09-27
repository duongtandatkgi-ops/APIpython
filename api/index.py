import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler
import yt_dlp
import cv2

def get_single_frame(video_url, resolution=32, timestamp_sec=0):
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
        return {"error": f"Lỗi link: {str(e)}"}

    cap = cv2.VideoCapture(stream_url)
    
    # LỆNH QUAN TRỌNG: Nhảy video đến đúng giây cần lấy (tính bằng milli-giây)
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return {"error": "Đã chạy hết video"}
        
    frame_resized = cv2.resize(frame, (resolution, resolution))
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    
    pixel_data = []
    for y in range(resolution):
        for x in range(resolution):
            r, g, b = frame_rgb[y, x]
            pixel_data.append({"x": x + 1, "y": y + 1, "r": int(r), "g": int(g), "b": int(b)})
            
    return pixel_data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        
        url = query.get('url', [''])[0]
        res = int(query.get('res', ['32'])[0])
        # Nhận tham số sec (giây thứ mấy của video), mặc định là 0
        sec = int(query.get('sec', ['0'])[0]) 
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if not url:
            self.wfile.write(json.dumps({"error": "Vui lòng cung cấp link url"}).encode('utf-8'))
            return
            
        data = get_single_frame(url, res, sec)
        self.wfile.write(json.dumps(data).encode('utf-8'))
