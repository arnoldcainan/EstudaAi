import re

_YT_PATTERNS = [
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([A-Za-z0-9_-]{11})",
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([A-Za-z0-9_-]{11})",
    r"(?:https?:\/\/)?youtu\.be\/([A-Za-z0-9_-]{11})"
]

def extract_youtube_id(url: str) -> str | None:
    if not url:
        return None
    for pat in _YT_PATTERNS:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    # fallback: se passar só o ID (11 chars)
    s = url.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    return None

def thumbnail_from_id(ytid: str) -> str:
    # hqdefault costuma ser ótima; pode trocar por maxresdefault.jpg
    return f"https://img.youtube.com/vi/{ytid}/hqdefault.jpg"

def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:80] or "geral"
