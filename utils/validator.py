import re

YOUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.)?'
    r'(youtube\.com/watch\?v=|youtube\.com/shorts/|youtu\.be/)'
    r'[\w\-]{11}'
)

def is_valid_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_REGEX.match(url))
