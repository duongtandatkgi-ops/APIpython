import requests
from fastapi import FastAPI

app = FastAPI()

# ... (Giữ nguyên các route cũ nếu có) ...


# API Trung Gian Lấy Dữ Liệu TikTok Cho Roblox
@app.get("/api/tiktok")
def get_tiktok(url: str):
  try:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    }
    # Gọi tới TikWM từ Python để tránh Cloudflare chặn Roblox
    res = requests.get(
        f'https://www.tikwm.com/api/?url={url}', headers=headers, timeout=10
    )
    data = res.json()

    if data.get('code') == 0 and 'data' in data:
      t_data = data['data']
      return {
          'success': True,
          'author': t_data.get('author', {}).get('nickname', 'Không rõ'),
          'unique_id': t_data.get('author', {}).get('unique_id', 'Không rõ'),
          'title': t_data.get('title', 'Không có tiêu đề'),
          'likes': t_data.get('digg_count', 0),
          'views': t_data.get('play_count', 0),
          'comments': t_data.get('comment_count', 0),
          'music': t_data.get('music_info', {}).get('title', 'Không có nhạc'),
      }
    else:
      return {
          'success': False,
          'error': data.get('msg', 'Link sai hoặc video riêng tư'),
      }

  except Exception as e:
    return {'success': False, 'error': str(e)}
