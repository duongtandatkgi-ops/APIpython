import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler
import urllib.request
import yt_dlp
import cv2

# Hàm trung gian vượt tường rào bảo mật TikTok
def get_tiktok_direct_url(tiktok_url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={tiktok_url}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            if res_data.get("code") == 0 and "data" in res_data:
                return res_data["data"]["play"] # Lấy đường dẫn MP4 trực tiếp
    except Exception:
        pass
    return None

def get_single_frame(video_url, resolution=32, timestamp_sec=0):
    stream_url = None
    
    # 1. Nếu là link TikTok, dùng TikWM để bypass chặn IP
    if "tiktok.com" in video_url:
        stream_url = get_tiktok_direct_url(video_url)
        
    # 2. Nếu không phải TikTok hoặc TikWM lỗi, dùng yt-dlp mặc định (cho YouTube)
    if not stream_url:
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
            return {"error": f"Server bị chặn IP: {str(e)}"}

    if not stream_url:
        return {"error": "Không tải được luồng video"}

    # 3. Trích xuất 1 khung hình qua OpenCV
    cap = cv2.VideoCapture(stream_url)
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
