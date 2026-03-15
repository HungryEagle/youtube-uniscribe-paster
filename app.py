import streamlit as st
import requests
import yt_dlp
import time

# ── Config ──────────────────────────────────────────────────────────────────
API_BASE = "https://api.uniscribe.co"
LANGUAGE  = "hi"          # Hindi, hardcoded
PASSWORD  = st.secrets["APP_PASSWORD"]
API_KEY   = st.secrets["UNISCRIBE_API_KEY"]

# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uniscribe Uploader",
    page_icon="🎙️",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        background-color: #0f0f0f;
        color: #f0ece4;
    }
    .stApp { background-color: #0f0f0f; }

    h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; color: #f0ece4; }

    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        background-color: #1a1a1a;
        border: 1px solid #333;
        color: #f0ece4;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
    }
    .stTextInput > div > div > input:focus,
    .stPasswordInput > div > div > input:focus {
        border-color: #c8a96e;
        box-shadow: 0 0 0 2px rgba(200,169,110,0.2);
    }

    .stButton > button {
        background-color: #c8a96e;
        color: #0f0f0f;
        border: none;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: background-color 0.2s;
        width: 100%;
    }
    .stButton > button:hover { background-color: #e0bf80; color: #0f0f0f; }

    .status-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: #1a1a1a;
        border-left: 3px solid #c8a96e;
        margin-bottom: 6px;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
    }
    .status-ok  { border-color: #4caf82; }
    .status-err { border-color: #e05c5c; }

    .label {
        color: #888;
        font-size: 0.75rem;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .divider { border: none; border-top: 1px solid #222; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Auth ─────────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("## 🎙️ Uniscribe Uploader")
    st.markdown('<div class="label">Password</div>', unsafe_allow_html=True)
    pw = st.text_input("", type="password", placeholder="Enter password…", label_visibility="collapsed")
    if st.button("Unlock"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()

# ── Main App ─────────────────────────────────────────────────────────────────
st.markdown("## 🎙️ Uniscribe Uploader")
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="label">YouTube URL — single video or playlist</div>', unsafe_allow_html=True)
url = st.text_input("", placeholder="https://www.youtube.com/playlist?list=...", label_visibility="collapsed")

submit = st.button("Send to Uniscribe →")

# ── Helpers ──────────────────────────────────────────────────────────────────
def extract_video_urls(playlist_url: str) -> list[dict]:
    """Return list of {url, title} for every video in the URL (works for single videos too)."""
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,   # don't download, just list
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    if "entries" in info:          # it's a playlist
        videos = []
        for entry in info["entries"]:
            if entry is None:
                continue
            vid_url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry['id']}"
            videos.append({"url": vid_url, "title": entry.get("title", vid_url)})
        return videos
    else:                          # single video
        return [{"url": playlist_url, "title": info.get("title", playlist_url)}]


def send_to_uniscribe(video_url: str, title: str) -> tuple[bool, str]:
    """POST one video to Uniscribe YouTube endpoint. Returns (success, message)."""
    payload = {
        "url": video_url,
        "language_code": LANGUAGE,
        "transcription_type": "transcript",
    }
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(f"{API_BASE}/api/v1/transcriptions/youtube", json=payload, headers=headers, timeout=30)
        data = r.json()
        if data.get("success"):
            return True, "Queued ✓"
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            return False, f"Error: {err}"
    except Exception as e:
        return False, f"Request failed: {e}"


# ── Submit logic ─────────────────────────────────────────────────────────────
if submit and url.strip():
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    with st.spinner("Fetching video list…"):
        try:
            videos = extract_video_urls(url.strip())
        except Exception as e:
            st.error(f"Could not read URL: {e}")
            st.stop()

    st.markdown(f'<div class="label">{len(videos)} video(s) found — sending to Uniscribe</div>', unsafe_allow_html=True)

    ok_count  = 0
    err_count = 0

    for i, vid in enumerate(videos, 1):
        success, msg = send_to_uniscribe(vid["url"], vid["title"])
        css_cls = "status-ok" if success else "status-err"
        icon    = "✓" if success else "✗"
        st.markdown(
            f'<div class="status-row {css_cls}">'
            f'<span>{icon}</span>'
            f'<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{vid["title"]}</span>'
            f'<span style="color:#888">{msg}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if success:
            ok_count += 1
        else:
            err_count += 1
        time.sleep(0.3)   # gentle rate limiting

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if err_count == 0:
        st.success(f"All {ok_count} video(s) sent! Open your Uniscribe dashboard to see them.")
    else:
        st.warning(f"{ok_count} sent, {err_count} failed. Check errors above.")

elif submit:
    st.warning("Please paste a YouTube URL first.")
