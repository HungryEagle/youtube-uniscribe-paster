# Uniscribe Uploader

A minimal Streamlit app for sending YouTube videos/playlists to Uniscribe for Hindi transcription.

## Deploy to Streamlit Cloud (free)

1. **Fork / push this repo to GitHub** (make sure `.gitignore` is included so secrets don't leak)

2. **Go to** [share.streamlit.io](https://share.streamlit.io) → New app → connect your GitHub repo → set main file as `app.py`

3. **Add secrets** in Streamlit Cloud:

4. **Deploy** — done.

## Usage

1. Open the app URL
2. Enter the password
3. Paste a YouTube video URL or playlist URL
4. Hit **Send to Uniscribe →**
5. Open [uniscribe.co](https://uniscribe.co) dashboard — all transcripts appear there in Hindi

## Local dev

```bash
pip install -r requirements.txt
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml with real values
streamlit run app.py
```
