import requests
from yt_dlp import YoutubeDL

def fetch_metadata(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title", "Unknown Title")
    thumb_url = info.get("thumbnail")

    img_data = None
    if thumb_url:
        img_data = requests.get(thumb_url).content

    return title, img_data
