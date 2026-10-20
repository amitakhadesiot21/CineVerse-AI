import streamlit as st
import pandas as pd
import requests
import pickle
import json
import os
import random
import urllib.parse
from datetime import datetime
import base64
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

# -------------------------------------------------
# PAGE CONFIG (must be first Streamlit call)
# -------------------------------------------------

st.set_page_config(
    page_title="CineVerse AI — Cinematic Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("styles.css not found — running with default Streamlit styling.")


load_css()

# PWA + mobile meta tags & self-contained install manifest
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#141414">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="CineVerse AI">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="data:application/json;base64,eyJuYW1lIjogIkNpbmVWZXJzZSBBSSIsICJzaG9ydF9uYW1lIjogIkNpbmVWZXJzZSIsICJkZXNjcmlwdGlvbiI6ICJBSS1Qb3dlcmVkIE1vdmllIERpc2NvdmVyeSAmIFJlY29tbWVuZGF0aW9uIFBsYXRmb3JtIiwgInN0YXJ0X3VybCI6ICIvIiwgInNjb3BlIjogIi8iLCAiZGlzcGxheSI6ICJzdGFuZGFsb25lIiwgIm9yaWVudGF0aW9uIjogInBvcnRyYWl0LXByaW1hcnkiLCAiYmFja2dyb3VuZF9jb2xvciI6ICIjMTQxNDE0IiwgInRoZW1lX2NvbG9yIjogIiNFNTA5MTQiLCAiaWNvbnMiOiBbeyJzcmMiOiAiZGF0YTppbWFnZS9wbmc7YmFzZTY0LGlWQk9SdzBLR2dvQUFBQU5TVWhFVWdBQUFNQUFBQURBQ0FZQUFBQlMzR3dIQUFBSlNVbEVRVlI0bk8yZHZYYmJSaENGUVI1TGpSc1ZlZ2x2d3k1TitqUitYamZwMDZSVHMzNE5OVzZrZ2ptVUF4dWlTUnJZbloyL2U3OUtQajZXdWNEOVptWkJFTnc5UGo0ZUowSkEyVnUvQUVJc29RQUVHZ3BBb0tFQUJCb0tRS0NoQUFRYUNrQ2dvUUFFbWcvV0x5QXpUOSttTDFLLzYvQngraXoxdThoUGRud24yRS9JVzZFYzdWQ0FnWUV2OTY5aVZidSszSzMrZnluRWVpaUFRT0FsZ3o1Q0RBcHhIUXF3TWZTV1laZVFnaks4aHdMOEp2UVJBdDhxeElFYmF3cHdLZmdaUXI5RmhnT3dDSkFkQUMzMDE2aVVBVXNBQnY4eUZWZ0VDQUhPZzQ5WTdWdGxPQ1FYSWJVQURINDdGVVNFbEFKNENuNTl1ZXYrSGVYK2RiS2lKaGNoblFETDhHc0ZYeUxrM3VXb0N4RXlTWkJHQU0ycWJ4bDRTeUZxd200UVhnQ3Q0SHNPdmJZTU5aRUlvUVVZUGU1RURMMm1ERFhCV0JSV2dGSGh6eFI2RFJscWNBbkNDYkExK01manorWHRkanZvNEo5VEtFSXNBYmFFZnhuOGM1WWlJQVovbEFnMVlEY0lJMEJQNWI4a0FJUC9LeElpUkpQQXZRQXRzLzZ0OE05OGZiM3ZmR1Y1S1VBaXVINHFoTVdiV21SNjY0NjlIWEo1dmp4OGJqcWNBQXgvZkJGS0FBbjJHY04vNjJyUENZNC8yNmlKSmRobnJQemM0UHJxQnNXeEJLNDJ3ZlBCNlpuM3owL1NwN3VYSHorejh0dHZrdXYvbTJNdkcyTTNBb3dJUHhsSFNTS0JDd0Y2dzgvZ3h4T2hPcEhBZkEvQThNZW1kdTRMclBjRXBnTDBMcDZWM3dlMWMvUzBsR0FmOVdvUHcrK0wyaUNCaDZ0REpnSXcvRG1wQVNVd0hZRlkrZk5ST3lWSUwwRFBwcGRqVDM0Sm5wUzdnS29BREQveEpvR2FBRDJMWXVYSHU1MzZTVWtDOVJGbzYrakQ4R09GdnlqdkIvYWVSeCtHSC9PamxVVnhGQm91QU1PUFFSRis3SXFXQkVNRmFIM3hyUHl4S0lNZnp6aFNBcFVSYU12b3cvREhvZ3dNdjhaK1lOamRvQng5K29QaXZSZ1U1UWZ6anJoejFOVTN4WHMvNFFhYlFiZkhxQmcrc3QxOUIyaXAvbDVPYk1EbjkwT3N0dzdxQW5zUEc1YW80VDhGd2JvU2FyK0dZcnhlNlEzeHNCRW82M044ckFPdzVuV05LaWpGY08yblBOMzZBbkFYSTFEbTBjZHI4TFdPYlhHeWZ1bFJ5UFIyYUlZLzdtWThDM3RQVDNYd2hvY1ozM29OeGRuNnBkOGhOdXNBM3F1L3R4TnZzWjZTN0JnTUV5QlQ5YzlROVNYV1Zod2ZBOGt1WU5JQnZGWi96eWRkYzUwRjVEaUlDSkNsK2lPZDlGdnJMVUdPZzFRWFVPOEFIcXQvbEpNK2V0MEY4RGlZUHhuT0dzU1RmbW45QmZRNDdEWEhIMi9WSC9Xa1p6a09SV0FNZ3UwQVVVODZrV1dQV1AwWi9qeVV6aTRBMXdFWWZxSXVnSmZxei9BVEVRR3lYUHNuT2VnWmcyQkdJTVRxLy96M245WXZ3VDE3aFBFSE1meGtrQUFjZjJKVmY1UXVVQnJIb1BRakVLcy9NUlBBZXZ4aCtNbUUzZ0VRUVJsNzFBV0lOUCt6K3VNSlVScjJBZnVzNHc4aGErQUlsQXlVYWk5RlNnRTQvaEJ4QWF5LzBwNzBnZFlabmxibWRYTUhXTE1CdHB6L1dmMnhLUnN2MEtRY2dWQkJxL0lTVUFBQ0RRVUFnaDBpdVFESTh6L0QzVVlxQVFnWklrQ2tXeUFJS1J0dWlSRHZBTHdGd3ZmNHcxSHBQUnlCQ0RTdXZpYTFCN1FOY0U4bFgvN2JoNy8rbVpCSkl3QUNJOGFYWjNBWlJBVTRIby9UcDd1WHQ1Ky92dDVML21wWU5HZjJaMEFaUGtnRi94eUtZQno4UHhZWFFQN2Rmdkh1R1VRR2prQVpxLzB5L1BPZkd5UkFrT0hEaU9wLzNnazREaW1PT09maEY1SWdxd3pzQUFaa3VSYi9uRUFHQ21EQU1peVJaWGdJR25wUkFYYTczYzB4aU9PUHNneW5NZWZTR0NRdy9tUUovUkoyZ0l3eW5FdlFHZjZIWktFWEYrRFVCVTRzT3dFci95UVN1bVlSR0hyOURuQVNnVGZEeGQwdlBDU3U5TmZnQ0FRdXd3Tmc2Rk1LY09vOFNEZkU5Y2lBSHZvbHZCMmFRQ011QUZJVjlzS1dpczdxM3lEQTRlUDBkaDJ0dnR6eDZYREVQWE5PNTl6ZWdpTVFnU2FWQU1pWFlEbmF0SkZLQUhJYlN2SXJGSUJBUXdFU3dRcXZJTUNhSzBHV2wwS1I5d0ZrMm55bGNyVUFheTRwRWIrZ2RZZkR5cnltSElIWUJjaGFVZ3FBREZxbGR5c0FiNGtnNlFTSWRFc0V4eUM4cmxBMzNBSXh3eEVvSVNpQmwyQ29BTlpqRUxzQW1kQTdBQ1Vnb2dKRTJnY2dNNDlCS09OUWJaai9WVHFBOVJoMGdsMkF3STVBeUJLZ1ZIOTFBVGdHa1F6amoxb0g4REFHb1hZQmNodVlFV2lHRWhBUkFiYU9RVjY2d0FsS2tJZmFNZjVBZG9BWlNrQzZCWWpjQlU1UWd0akhvYmY2UTNlQTZDZGZldjBWOURpb0MrQ3RDeUNmL0hxMmJzVGowQzFBbHZjRTBFNyt0ZlhXSU1kQll2d3hHNEU4ZG9GSUozLzBPaXZJY1JBVElFc1htRTkrMWdCc1dWdDFmQXlrcXIvcEp0aHJGNGdRQUszMTFHVEhZS2dBbWJwQXBtN1F1NGJxYlAyUzFkLzhNcWozTHVBMUJOcXZ1d1pkL3hwMmo0K1AxNy9rdDRHbmI5T2JvZVgrOVhQR0F4eEIybEhIczloL3hGVzArZy90QUpsR29Vc2poVGRwTlY1WE5WenpxRHlKQzlCaXAzVmxhY1dEQ05xdm9ScXZWL29SbmVJakVNb29aQ1cwbDJOVUZJdldpTkhINWRla25nNnFseFBjdzZVMXRBVEc4N0dvU2I2V2RsZ0hRTzhDS0pUQkVveXMvbXFYUWJkc1lESlVGU1RxMkUzMzhBc3BRd1ZvdFpZU3hLSU83dG9qdjV0aWVBZG9mWWVZRW1CTFVBZVBQcW9qRUNYQW9NcTk4NndTZnBOYklkZ0pjbE03SmRCK0ExVk5nQjZiT1E3aGRZS0QwbmZTcVhhQW5qdEdLVUYrcXVMb1l6WUNVWUw4bExZMy9kVERiMzQ3TkR0QlBrcEgrQzB3RVdCcE9TWElRK2tNdjhWM1VadDFBRXFRaXhJdy9PWWpVTytpdVRIMlFlbThmY1VxL0M2ZUROZjdXV0pLWUV0cERML1ZwbGYxYnREUmQ0NnV2Zjc4NmU3bHg4OWZYKzliZnowUktqeGV3dTlLZ0JFU0xJTi9Ea1ZvSjB2NDNRbXdsS0JIaEZrQ0N1QnY1UEVVZnBjQ1NFbHdQUDUrV2V3Q3VsWGZXL2hkYklKSFhDSWxzcFNrNFhjcndBbEs0Q1A0SlhINFhRdlFLOEZ1dDd2NTl4eC9ydE1iL0NqaGQ3c0hrTm9YM05vSFVJQmZrWGhQSlVyd3d3blFzemxlaW5EZUdmZ1Vpa25zemNSbzRROG5nTlFWb2tzZ2lsQUVuOEFSTWZ3aEJaaWhDTzB3K0FrRUdDbEJ4cTR3NHA2cEdyVHFweEhnWElKUklrU1ZZZFNOZ3ZYc2lselU4S2NRUUZzRTd6SU1makR2bHl6QlR5ZUExbGprVFFpdDI4RnJnbkVIUWdEdGJxQWhoK1ZuSG1yQ3FwOWVBSThpUktNbUR6NkVBRE1VWVQwVkpQaFFBbHdUNFFTN3duVHhQcXZzd1ljVVlJWWlmS2NDQng5YUFHUVpHUHIzd0F0d1M0UXNNbHk3bGZ3QVZ1MHZRUUUyeUJCRmlGdWZuV0RvMzBNQk9tUnc4ajdEYjE4ZlEzOGRDakJBaUVHM2E2LytmeG40OVZBQVJTRkd3Y0MzUXdHQ3lNR1FqNEVDRUdoY1B4V0NrTkZRQUFJTkJTRFFVQUFDRFFVZzBGQUFBZzBGSUJNeS93SHBJMmp2VWJ4Z1ZRQUFBQUJKUlU1RXJrSmdnZz09IiwgInNpemVzIjogIjE5MngxOTIiLCAidHlwZSI6ICJpbWFnZS9wbmciLCAicHVycG9zZSI6ICJhbnkgbWFza2FibGUifV19">
""", unsafe_allow_html=True)


def render_opening_intro():
    """Cinematic studio intro opening animation with lens flare and emblem reveal."""
    st.html("""
    <div id="cv-splash-overlay" class="cv-splash" onclick="dismissCvSplash()">
      <div class="cv-splash-bg"></div>
      <div class="cv-splash-flare"></div>
      <div class="cv-splash-content">
        <div class="cv-splash-emblem">
          <svg viewBox="0 0 100 100" width="96" height="96" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="46" fill="url(#introGlow)" opacity="0.5"/>
            <path d="M64,18 C42,18 24,32 24,50 C24,68 42,82 64,82 C74,82 82,78 88,71 L75,59 C72,63 68,66 64,66 C51,66 40,58 40,50 C40,42 51,34 64,34 C68,34 72,37 75,41 L88,29 C82,22 74,18 64,18 Z" fill="url(#introRed)"/>
            <rect x="29" y="34" width="4.5" height="7" rx="1.5" fill="#141414"/>
            <rect x="26.5" y="46.5" width="4.5" height="7" rx="1.5" fill="#141414"/>
            <rect x="29" y="59" width="4.5" height="7" rx="1.5" fill="#141414"/>
            <path d="M64,39 L67,48 L76,50 L67,52 L64,61 L61,52 L52,50 L61,48 Z" fill="url(#introGold)"/>
            <circle cx="64" cy="50" r="2.8" fill="#FFFFFF"/>
            <defs>
              <radialGradient id="introGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#E50914"/>
                <stop offset="100%" stop-color="#0A0A0C" stop-opacity="0"/>
              </radialGradient>
              <linearGradient id="introRed" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FF3B4E"/>
                <stop offset="50%" stop-color="#E50914"/>
                <stop offset="100%" stop-color="#800006"/>
              </linearGradient>
              <linearGradient id="introGold" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FFF0A0"/>
                <stop offset="100%" stop-color="#FFC94A"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="cv-splash-wordmark">
          <span class="cv-letter">C</span>
          <span class="cv-letter">I</span>
          <span class="cv-letter">N</span>
          <span class="cv-letter">E</span>
          <span class="cv-letter red">V</span>
          <span class="cv-letter red">E</span>
          <span class="cv-letter red">R</span>
          <span class="cv-letter red">S</span>
          <span class="cv-letter red">E</span>
          <span class="cv-splash-badge">AI</span>
        </div>
        <div class="cv-splash-tagline">YOUR CINEMATIC UNIVERSE • POWERED BY AI</div>
        <div class="cv-splash-bar"><div class="cv-splash-bar-fill"></div></div>
        <div class="cv-splash-status">INITIALIZING AI ENGINE & CURATING SPOTLIGHT...</div>
      </div>
      <button class="cv-splash-skip" onclick="event.stopPropagation(); dismissCvSplash();">✕ Skip</button>
    </div>

    <script>
    function dismissCvSplash() {
        var el = document.getElementById('cv-splash-overlay');
        if (el) {
            el.classList.add('cv-dismissed');
            setTimeout(function() { el.style.display = 'none'; }, 400);
        }
    }
    setTimeout(dismissCvSplash, 3600);
    </script>
    """)


if not st.session_state.get("intro_shown", False):
    st.session_state.intro_shown = True
    render_opening_intro()


def render_brand_navbar():
    """Renders the top sleek brand navigation bar with SVG emblem."""
    st.html("""
    <div class="cv-brand-nav">
        <div class="cv-brand-logo-group">
            <svg viewBox="0 0 100 100" class="cv-brand-emblem-svg" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="46" fill="url(#navGlow)" opacity="0.4"/>
              <path d="M64,18 C42,18 24,32 24,50 C24,68 42,82 64,82 C74,82 82,78 88,71 L75,59 C72,63 68,66 64,66 C51,66 40,58 40,50 C40,42 51,34 64,34 C68,34 72,37 75,41 L88,29 C82,22 74,18 64,18 Z" fill="url(#navRed)"/>
              <rect x="29" y="34" width="4.5" height="7" rx="1.5" fill="#141414"/>
              <rect x="26.5" y="46.5" width="4.5" height="7" rx="1.5" fill="#141414"/>
              <rect x="29" y="59" width="4.5" height="7" rx="1.5" fill="#141414"/>
              <path d="M64,39 L67,48 L76,50 L67,52 L64,61 L61,52 L52,50 L61,48 Z" fill="url(#navGold)"/>
              <circle cx="64" cy="50" r="2.8" fill="#FFFFFF"/>
              <defs>
                <radialGradient id="navGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stop-color="#E50914"/>
                  <stop offset="100%" stop-color="#141414" stop-opacity="0"/>
                </radialGradient>
                <linearGradient id="navRed" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#FF3B4E"/>
                  <stop offset="50%" stop-color="#E50914"/>
                  <stop offset="100%" stop-color="#800006"/>
                </linearGradient>
                <linearGradient id="navGold" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#FFF0A0"/>
                  <stop offset="100%" stop-color="#FFC94A"/>
                </linearGradient>
              </defs>
            </svg>
            <div class="cv-brand-name">
                CINE<span class="accent">VERSE</span>
                <span class="cv-brand-badge">AI</span>
            </div>
        </div>
        <div class="cv-brand-live">
            <span class="cv-live-dot"></span>
            <span>AI Ready</span>
        </div>
    </div>
    """)

# -------------------------------------------------
# TMDB API KEY & PLATFORM URLS
# -------------------------------------------------

API_KEY = st.secrets["TMDB_API_KEY"]

TMDB_BASE = "https://api.themoviedb.org/3"
DATA_FILE = "user_data.json"

PLATFORM_URLS = {
    "Netflix": "https://www.netflix.com/search?q={query}",
    "Amazon Prime Video": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase={query}",
    "Hotstar": "https://www.hotstar.com/in/explore?search_query={query}",
    "Disney Plus": "https://www.disneyplus.com/search?q={query}",
    "JioCinema": "https://www.jiocinema.com/search/{query}",
    "Apple TV": "https://tv.apple.com/search?term={query}",
    "Apple TV Plus": "https://tv.apple.com/search?term={query}",
    "Hulu": "https://www.hulu.com/search?q={query}",
    "Max": "https://play.max.com/search?q={query}",
    "Sony Liv": "https://www.sonyliv.com/search?q={query}",
    "Zee5": "https://www.zee5.com/search?q={query}",
}

# -------------------------------------------------
# LOAD DATA (cached so the pickle only loads once per session)
# -------------------------------------------------

from huggingface_hub import hf_hub_download

@st.cache_resource
def load_movie_data():
    movie_data_path = hf_hub_download(
        repo_id="ClashOfCrush/cineverse-movie-data",
        filename="movie_data.pkl"
    )

    with open(movie_data_path, "rb") as file:
        return pickle.load(file)

try:
    movies, cosine_sim = load_movie_data()
except Exception as e:
    st.error(f"⚠️ Could not load movie data: {e}")
    st.stop()

# -------------------------------------------------
# PERSISTENCE
# -------------------------------------------------
# Favorites/watchlist/history/ratings are saved to a local JSON file so they
# survive a page refresh or app restart. Note: this is a single shared file,
# so if you deploy this for multiple people, everyone shares the same lists —
# swap this for a real per-user database if that matters for your use case.


def load_user_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"favorites": [], "watchlist": [], "history": [], "ratings": {}}


def save_user_data():
    data = {
        "favorites": st.session_state.favorites,
        "watchlist": st.session_state.watchlist,
        "history": st.session_state.history,
        "ratings": st.session_state.ratings,
    }
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass  # e.g. read-only filesystem — app still works, just won't persist


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "data_loaded" not in st.session_state:
    saved = load_user_data()
    st.session_state.favorites = saved.get("favorites", [])
    st.session_state.watchlist = saved.get("watchlist", [])
    st.session_state.history = saved.get("history", [])
    st.session_state.ratings = saved.get("ratings", {})
    st.session_state.data_loaded = True

if "random_movie" not in st.session_state:
    st.session_state.random_movie = movies.sample(1).iloc[0]

# -------------------------------------------------
# FUNCTIONS
# -------------------------------------------------


def make_fallback_poster_svg(title="Movie"):
    safe_title = (
        (str(title) if title else "Movie")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', '&quot;')
    )
    if len(safe_title) > 26:
        display_title = safe_title[:24] + "..."
    else:
        display_title = safe_title

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="450" viewBox="0 0 300 450">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#12151C"/>
      <stop offset="50%" stop-color="#1B1F2A"/>
      <stop offset="100%" stop-color="#0A0C10"/>
    </linearGradient>
  </defs>
  <rect width="300" height="450" fill="url(#bg)"/>
  <rect x="10" y="10" width="280" height="430" rx="16" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="2"/>
  <circle cx="150" cy="180" r="50" fill="#232837" stroke="rgba(229,9,20,0.4)" stroke-width="2"/>
  <text x="150" y="195" font-size="40" text-anchor="middle" fill="#E50914" font-family="'Segoe UI', Roboto, sans-serif">&#127916;</text>
  <text x="150" y="270" font-size="16" font-weight="bold" text-anchor="middle" fill="#F5F6FA" font-family="'Segoe UI', Roboto, sans-serif">{display_title}</text>
  <text x="150" y="298" font-size="12" text-anchor="middle" fill="#9AA1B1" font-family="'Segoe UI', Roboto, sans-serif">No Poster Available</text>
  <rect x="95" y="380" width="110" height="26" rx="13" fill="rgba(229,9,20,0.15)" stroke="#E50914" stroke-width="1"/>
  <text x="150" y="397" font-size="11" font-weight="bold" text-anchor="middle" fill="#FF3B4E" font-family="'Segoe UI', Roboto, sans-serif">CINEVERSE</text>
</svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")


def make_fallback_avatar_svg(name="?"):
    safe_name = str(name).strip() if name else "?"
    initial = (safe_name[:1] if safe_name else "?").upper()
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <rect width="200" height="200" fill="#1B1F2A"/>
  <circle cx="100" cy="100" r="70" fill="#232837"/>
  <text x="100" y="118" font-size="52" font-weight="bold" text-anchor="middle" fill="#FFC94A" font-family="'Segoe UI', Roboto, sans-serif">{initial}</text>
</svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")


@st.cache_resource
def get_tmdb_session():
    """Shared requests.Session with connection pooling, browser User-Agent,
    and automatic retries with backoff to prevent WinError 10054 connection resets."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
    })
    retries = Retry(
        total=3,
        backoff_factor=0.4,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=20, pool_maxsize=40)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_movie(movie_id, title=None):
    """Fetch poster/rating/overview/genres for a movie with resilient session,
    automatic retry, title-search fallback, and inline SVG fallback."""
    session = get_tmdb_session()
    data = None

    # 1. Try fetching by TMDB movie_id
    try:
        url = f"{TMDB_BASE}/movie/{movie_id}"
        resp = session.get(url, params={"api_key": API_KEY}, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
    except Exception:
        data = None

    # 2. If ID lookup failed or returned no poster, fallback to searching TMDB by title
    if (not data or not data.get("poster_path")) and title:
        try:
            search_url = f"{TMDB_BASE}/search/movie"
            resp = session.get(
                search_url,
                params={"api_key": API_KEY, "query": str(title), "include_adult": False},
                timeout=8,
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    exact = [m for m in results if m.get("title", "").strip().lower() == str(title).strip().lower()]
                    match = exact[0] if exact else results[0]
                    if not data:
                        data = match
                    elif match.get("poster_path"):
                        data["poster_path"] = match.get("poster_path")
        except Exception:
            pass

    display_title = title or (data.get("title") if data else "Movie")
    fallback_poster = make_fallback_poster_svg(display_title)

    if not data:
        return (
            fallback_poster,
            "NR",
            "Unknown",
            "Movie details are currently unavailable.",
            "Unknown",
        )

    poster = (
        "https://image.tmdb.org/t/p/w500" + data["poster_path"]
        if data.get("poster_path")
        else fallback_poster
    )

    vote_avg = data.get("vote_average")
    if vote_avg is not None and isinstance(vote_avg, (int, float)) and vote_avg > 0:
        rating = round(float(vote_avg), 1)
    else:
        rating = "NR"

    release = data.get("release_date") or "Unknown"
    overview = data.get("overview") or "No description available."
    genres_list = data.get("genres", [])
    if genres_list and isinstance(genres_list[0], dict):
        genres = ", ".join(g["name"] for g in genres_list)
    elif "genre_ids" in data:
        genres = "Movie"
    else:
        genres = "Unknown"

    return poster, rating, release, overview, genres


@st.cache_data(ttl=86400, show_spinner=False)
def get_trailer_url(movie_id):
    """Official YouTube trailer URL, or None if not found."""
    try:
        session = get_tmdb_session()
        r = session.get(f"{TMDB_BASE}/movie/{movie_id}/videos", params={"api_key": API_KEY}, timeout=8)
        if r.status_code != 200:
            return None
        vids = r.json().get("results", [])
        trailers = [v for v in vids if v.get("type") == "Trailer" and v.get("site") == "YouTube"]
        if not trailers:
            return None
        official = [v for v in trailers if v.get("official")]
        pick = official[0] if official else trailers[0]
        return f"https://www.youtube.com/watch?v={pick['key']}"
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_streaming_info(movie_id, title, region="IN"):
    """
    Fetches the primary streaming provider from TMDB for the given region (defaults to 'IN',
    falls back to 'US') and returns (platform_name, direct_redirect_url).
    """
    encoded_title = urllib.parse.quote_plus(str(title))
    try:
        session = get_tmdb_session()
        r = session.get(
            f"{TMDB_BASE}/movie/{movie_id}/watch/providers",
            params={"api_key": API_KEY},
            timeout=8,
        )
        if r.status_code == 200:
            results = r.json().get("results", {})
            region_data = (
                results.get(region)
                or results.get("US")
                or (next(iter(results.values())) if results else {})
            )

            providers = (
                region_data.get("flatrate")
                or region_data.get("rent")
                or region_data.get("buy")
                or []
            )

            if providers:
                provider_name = providers[0].get("provider_name", "Stream")
                for key, url_template in PLATFORM_URLS.items():
                    if key.lower() in provider_name.lower():
                        return provider_name, url_template.format(query=encoded_title)

                tmdb_watch_link = region_data.get("link")
                if tmdb_watch_link:
                    return provider_name, tmdb_watch_link
    except Exception:
        pass

    return "Netflix", f"https://www.netflix.com/search?q={encoded_title}"


@st.cache_data(ttl=86400, show_spinner=False)
def get_runtime(movie_id):
    """Fetch movie runtime in minutes from TMDB."""
    try:
        session = get_tmdb_session()
        r = session.get(f"{TMDB_BASE}/movie/{movie_id}", params={"api_key": API_KEY}, timeout=8)
        if r.status_code == 200:
            val = r.json().get("runtime")
            if val:
                return val
    except Exception:
        pass
    return "N/A"


def get_card_action_links(movie_id, title):
    """Returns (trailer_url, provider_name, watch_url) with safe fallbacks."""
    trailer_url = get_trailer_url(movie_id)
    if not trailer_url:
        encoded = urllib.parse.quote_plus(f"{title} official trailer")
        trailer_url = f"https://www.youtube.com/results?search_query={encoded}"

    provider_name, watch_url = get_streaming_info(movie_id, title)
    return trailer_url, provider_name, watch_url


def recommend(movie_title, top_n=10):
    idx = movies[movies["title"] == movie_title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1: top_n + 1]
    movie_indices = [i[0] for i in sim_scores]
    result = movies.iloc[movie_indices].copy()
    result["match_score"] = [round(s[1] * 100) for s in sim_scores]
    return result


def toggle_list(title, list_name, icon):
    """Add/remove a movie from favorites or watchlist and give feedback."""
    lst = st.session_state[list_name]
    if title in lst:
        lst.remove(title)
        st.toast(f"Removed from {list_name.capitalize()}", icon="💔")
    else:
        lst.append(title)
        st.toast(f"Added to {list_name.capitalize()}!", icon=icon)
        if list_name == "favorites":
            st.balloons()
    save_user_data()


def list_button(title, list_name, label, icon, key):
    is_in = title in st.session_state[list_name]
    clean_label = str(label).strip()
    # Strip any duplicate emojis that might be passed in label
    for prefix in [icon, "❤️", "📋", "⭐", "✔", "✓"]:
        if clean_label.startswith(prefix):
            clean_label = clean_label[len(prefix):].strip()

    btn_label = f"✓ In {clean_label}" if is_in else f"{icon} {clean_label}"
    if st.button(btn_label, key=key, use_container_width=True):
        toggle_list(title, list_name, icon)
        st.rerun()


def rating_bucket(rating):
    try:
        val = float(rating)
    except (TypeError, ValueError):
        return "mid"
    if val >= 7:
        return "high"
    if val >= 5:
        return "mid"
    return "low"


def is_new_release(year_str):
    """True if a movie released this year or last — used for the NEW ribbon."""
    try:
        y = int(year_str)
    except (TypeError, ValueError):
        return False
    return y >= datetime.now().year - 1


def esc(text):
    """Escape text before dropping it into raw HTML blocks."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_grid_card(movie, col, index, key_prefix="grid"):
    movie_id = movie["movie_id"]
    raw_title = str(movie["title"])
    moviePoster, movieRating, movieRelease, _, movieGenres = fetch_movie(movie_id, title=raw_title)
    trailer_url, provider_name, watch_url = get_card_action_links(movie_id, raw_title)

    year = movieRelease[:4] if movieRelease and movieRelease != "Unknown" else "N/A"

    # NEW ribbon
    ribbon_html = (
        '<span class="new-ribbon">NEW</span>'
        if is_new_release(year)
        else ""
    )

    # Match score
    match_html = ""
    if "match_score" in movie.index and pd.notna(movie.get("match_score")):
        score = int(movie["match_score"])
        match_html = f"""
            <div class="match-section">
                <div class="match-bar-track">
                    <div class="match-bar-fill" style="width:{score}%"></div>
                </div>
                <div class="match-label">
                    🎯 {score}% Match
                </div>
            </div>
        """

    # Rating
    try:
        rating_display = round(float(movieRating), 1)
    except Exception:
        rating_display = movieRating

    rating_class = rating_bucket(movieRating)

    # Genre
    genre = (
        movieGenres.split(",")[0].strip()
        if movieGenres and movieGenres != "Unknown"
        else "Movie"
    )

    # Escape text that comes from movie data
    title = esc(raw_title)
    safe_provider = esc(provider_name)
    fallback_poster = make_fallback_poster_svg(raw_title)

    card_html = f"""
    <div class="poster-card">

        <img
            src="{moviePoster}"
            class="poster-image"
            alt="{title}"
            loading="lazy"
            onerror="this.onerror=null;this.src='{fallback_poster}';"
        >

        {ribbon_html}

        <span class="rating-badge {rating_class}">
            ⭐ {rating_display}
        </span>

        <div class="card-overlay">

            <h4 class="movie-title">
                {title}
            </h4>

            <div class="card-meta">
                📅 {year}
                &nbsp;•&nbsp;
                🎭 {genre}
            </div>

            {match_html}

            <div class="card-actions">
                <a href="{trailer_url}" target="_blank" rel="noopener noreferrer" class="card-btn btn-trailer" title="Watch Official Trailer">
                    ▶ Trailer
                </a>
                <a href="{watch_url}" target="_blank" rel="noopener noreferrer" class="card-btn btn-watch" title="Watch on {safe_provider}">
                    🍿 Watch
                </a>
            </div>

        </div>

    </div>
    """

    with col:
        # IMPORTANT: Use st.html instead of st.markdown
        st.html(card_html)

        list_button(
            raw_title,
            "favorites",
            "Fav",
            "❤️",
            key=f"{key_prefix}_fav_{index}_{movie_id}"
        )


@st.cache_data(ttl=86400, show_spinner=False)
def get_genre_map():
    """name -> id, for the genre filter UI."""
    try:
        session = get_tmdb_session()
        r = session.get(f"{TMDB_BASE}/genre/movie/list", params={"api_key": API_KEY}, timeout=8)
        if r.status_code != 200:
            return {}
        return {g["name"]: g["id"] for g in r.json().get("genres", [])}
    except Exception:
        return {}


@st.cache_data(ttl=3600, show_spinner=False)
def discover_movies(mode="trending", genre_id=None):
    """Fetch a page of movies for Trending / Top Rated / By Genre browsing.
    Returns raw TMDB result dicts (title, poster_path, vote_average, release_date, id)."""
    try:
        session = get_tmdb_session()
        if mode == "trending":
            url, params = f"{TMDB_BASE}/trending/movie/week", {"api_key": API_KEY}
        elif mode == "top_rated":
            url, params = f"{TMDB_BASE}/movie/top_rated", {"api_key": API_KEY}
        else:
            url = f"{TMDB_BASE}/discover/movie"
            params = {"api_key": API_KEY, "with_genres": genre_id, "sort_by": "popularity.desc"}

        r = session.get(url, params=params, timeout=8)
        if r.status_code != 200:
            return []
        return r.json().get("results", [])[:10]
    except Exception:
        return []


@st.cache_data(ttl=86400, show_spinner=False)
def get_credits(movie_id):
    """Top billed cast for a movie, with headshots."""
    try:
        session = get_tmdb_session()
        r = session.get(f"{TMDB_BASE}/movie/{movie_id}/credits", params={"api_key": API_KEY}, timeout=8)
        if r.status_code != 200:
            return []
        cast = r.json().get("cast", [])[:8]
        return [
            {
                "name": c["name"],
                "character": c.get("character", ""),
                "profile": (
                    "https://image.tmdb.org/t/p/w200" + c["profile_path"]
                    if c.get("profile_path")
                    else make_fallback_avatar_svg(c["name"])
                ),
            }
            for c in cast
        ]
    except Exception:
        return []


@st.cache_data(ttl=86400, show_spinner=False)
def find_tmdb_movie(title):
    """Find a TMDB movie ID using its title."""
    try:
        session = get_tmdb_session()
        r = session.get(
            f"{TMDB_BASE}/search/movie",
            params={
                "api_key": API_KEY,
                "query": title,
                "include_adult": False,
            },
            timeout=8,
        )

        if r.status_code != 200:
            return None

        results = r.json().get("results", [])

        if not results:
            return None

        # Prefer exact title match
        exact = [
            m for m in results
            if m.get("title", "").lower() == title.lower()
        ]

        return (exact[0] if exact else results[0])

    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_tmdb_recommendations(movie_id, limit=5):
    """Get TMDB recommendations for a movie."""
    try:
        session = get_tmdb_session()
        r = session.get(
            f"{TMDB_BASE}/movie/{movie_id}/recommendations",
            params={
                "api_key": API_KEY,
            },
            timeout=8,
        )

        if r.status_code != 200:
            return []

        results = r.json().get("results", [])

        # Only keep movies with posters
        results = [
            m for m in results
            if m.get("poster_path")
        ]

        return results[:limit]

    except Exception:
        return []


def render_trailer_block(movie_id, fallback_title):
    trailer_url = get_trailer_url(movie_id)
    if trailer_url:
        st.video(trailer_url)
    else:
        search_link = (
            "https://www.youtube.com/results?search_query="
            + fallback_title.replace(" ", "+")
            + "+official+trailer"
        )
        st.caption("No trailer on file for this one.")
        st.link_button("▶ Search on YouTube", search_link, use_container_width=True)


def render_cast_row(cast):
    if not cast:
        st.caption("No cast info available.")
        return
    chips = "".join(
        f"""<div class="cast-chip">
                <div class="cast-avatar" style="background-image:url('{c['profile']}')"></div>
                <div class="cast-name">{c['name']}</div>
                <div class="cast-role">{c['character']}</div>
            </div>"""
        for c in cast
    )
    st.markdown(f'<div class="carousel-row">{chips}</div>', unsafe_allow_html=True)


def rate_movie(title, key):
    current = st.session_state.ratings.get(title, 0)
    new_val = st.slider("Your rating", 0, 5, value=current, key=key, help="0 = not rated")
    if new_val != current:
        if new_val == 0:
            st.session_state.ratings.pop(title, None)
        else:
            st.session_state.ratings[title] = new_val
        save_user_data()
    display = st.session_state.ratings.get(title, 0)
    st.markdown("⭐" * display + "☆" * (5 - display))


def render_discover_card(movie, col, index, key_prefix):
    movie_id = movie.get("id")
    title = movie.get("title") or movie.get("name") or "Unknown"
    fallback_poster = make_fallback_poster_svg(title)
    poster = (
        "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
        if movie.get("poster_path")
        else fallback_poster
    )

    rating = movie.get("vote_average", "NR")
    if isinstance(rating, (int, float)) and rating > 0:
        rating_display = round(rating, 1)
    elif rating == "NR":
        rating_display = "NR"
    else:
        rating_display = rating or "NR"

    year = (movie.get("release_date") or "")[:4] or "N/A"

    ribbon_html = (
        '<span class="new-ribbon">NEW</span>'
        if is_new_release(year)
        else ""
    )

    rating_class = rating_bucket(rating)

    trailer_url, provider_name, watch_url = get_card_action_links(movie_id, title)
    safe_title = esc(title)
    safe_provider = esc(provider_name)

    card_html = f"""
    <div class="poster-card">

        <img
            src="{poster}"
            class="poster-image"
            alt="{safe_title}"
            loading="lazy"
            onerror="this.onerror=null;this.src='{fallback_poster}';"
        >

        {ribbon_html}

        <span class="rating-badge {rating_class}">
            ⭐ {rating_display}
        </span>

        <div class="card-overlay">

            <h4 class="movie-title">
                {safe_title}
            </h4>

            <div class="card-meta">
                📅 {year}
            </div>

            <div class="card-actions">
                <a href="{trailer_url}" target="_blank" rel="noopener noreferrer" class="card-btn btn-trailer" title="Watch Official Trailer">
                    ▶ Trailer
                </a>
                <a href="{watch_url}" target="_blank" rel="noopener noreferrer" class="card-btn btn-watch" title="Watch on {safe_provider}">
                    🍿 Watch
                </a>
            </div>

        </div>

    </div>
    """

    with col:
        st.html(card_html)

        list_button(
            title,
            "favorites",
            "Fav",
            "❤️",
            key=f"{key_prefix}_fav_{index}_{movie_id}"
        )



# -------------------------------------------------
# SIDEBAR  (Netflix-style compact)
# -------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div class="sb-header">
        <svg viewBox="0 0 100 100" class="cv-brand-emblem-svg" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:36px; height:36px;">
          <circle cx="50" cy="50" r="46" fill="#1B1F2A"/>
          <path d="M64,18 C42,18 24,32 24,50 C24,68 42,82 64,82 C74,82 82,78 88,71 L75,59 C72,63 68,66 64,66 C51,66 40,58 40,50 C40,42 51,34 64,34 C68,34 72,37 75,41 L88,29 C82,22 74,18 64,18 Z" fill="#E50914"/>
          <rect x="29" y="34" width="4.5" height="7" rx="1.5" fill="#141414"/>
          <rect x="26.5" y="46.5" width="4.5" height="7" rx="1.5" fill="#141414"/>
          <rect x="29" y="59" width="4.5" height="7" rx="1.5" fill="#141414"/>
          <path d="M64,39 L67,48 L76,50 L67,52 L64,61 L61,52 L52,50 L61,48 Z" fill="#FFC94A"/>
          <circle cx="64" cy="50" r="2.8" fill="#FFFFFF"/>
        </svg>
        <div>
            <h2 class="sb-title">CineVerse AI</h2>
            <span class="sb-status">● Engine Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Quick Stats
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.metric("🎞️ Catalog", f"{len(movies):,}")
        st.metric("❤️ Favs", len(st.session_state.favorites))
    with s_col2:
        st.metric("📋 Watchlist", len(st.session_state.watchlist))
        avg_r = (
            round(sum(st.session_state.ratings.values()) / len(st.session_state.ratings), 1)
            if st.session_state.ratings else "–"
        )
        st.metric("⭐ Avg", avg_r)

    st.divider()

    # Surprise
    st.markdown("### 🎲 Quick Spin")
    if st.button("✨ Surprise Movie", use_container_width=True, key="sb_surprise"):
        st.session_state.random_movie = movies.sample(1).iloc[0]
        st.rerun()

    rand_m = st.session_state.random_movie
    p_poster, p_rating, p_release, _, _ = fetch_movie(rand_m["movie_id"], title=rand_m["title"])
    p_year = p_release[:4] if p_release and p_release != "Unknown" else "N/A"
    p_fallback = make_fallback_poster_svg(rand_m["title"])
    st.html(f"""
        <div class="sb-surprise-card">
            <img src="{p_poster}" class="sb-surprise-img" alt="{esc(rand_m['title'])}" onerror="this.onerror=null;this.src='{p_fallback}';">
            <div class="sb-surprise-info">
                <div class="sb-surprise-title">{esc(rand_m['title'])}</div>
                <div class="sb-surprise-meta">⭐ {p_rating} • 📅 {p_year}</div>
            </div>
        </div>
    """)

    if st.button("🎬 Replay Opening Intro", use_container_width=True, key="sb_replay_intro"):
        st.session_state.intro_shown = False
        st.rerun()

    st.divider()

    def render_sidebar_movie_item(title_text, list_name, key_prefix):
        matched = movies[movies["title"] == title_text]
        m_id = matched.iloc[0]["movie_id"] if not matched.empty else None
        poster_url, rating, release, _, _ = fetch_movie(m_id, title=title_text)
        year = release[:4] if release and release != "Unknown" else "N/A"
        fallback = make_fallback_poster_svg(title_text)

        c_info, c_del = st.columns([5, 1])
        with c_info:
            st.html(f"""
                <div class="sb-fav-card">
                    <img src="{poster_url}" class="sb-fav-poster" alt="{esc(title_text)}" onerror="this.onerror=null;this.src='{fallback}';">
                    <div class="sb-fav-info">
                        <div class="sb-fav-title" title="{esc(title_text)}">{esc(title_text)}</div>
                        <div class="sb-fav-meta">⭐ {rating} • 📅 {year}</div>
                    </div>
                </div>
            """)
        with c_del:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("✕", key=f"{key_prefix}_del_{title_text}"):
                st.session_state[list_name].remove(title_text)
                save_user_data()
                st.rerun()

    with st.expander("❤️ Favorites", expanded=False):
        if not st.session_state.favorites:
            st.caption("No favorites yet.")
        else:
            for fav_title in st.session_state.favorites[:6]:
                render_sidebar_movie_item(fav_title, "favorites", "sb_fav")
            if len(st.session_state.favorites) > 6:
                st.caption(f"…and {len(st.session_state.favorites) - 6} more in **My Lists**.")

    with st.expander("📋 Watchlist", expanded=False):
        if not st.session_state.watchlist:
            st.caption("Watchlist is empty.")
        else:
            for watch_title in st.session_state.watchlist[:6]:
                render_sidebar_movie_item(watch_title, "watchlist", "sb_watch")
            if len(st.session_state.watchlist) > 6:
                st.caption(f"…and {len(st.session_state.watchlist) - 6} more in **My Lists**.")

    st.divider()
    st.markdown("""
    <div class="sb-footer">
        <div class="sb-footer-badge">Developed by <b>Amit Akhade</b></div>
        <div class="sb-footer-sub">Final Year Project • 2026</div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------
# NETFLIX HORIZONTAL CAROUSEL ROW HELPER
# -------------------------------------------------

def render_nf_row(title: str, movies_list, key_prefix: str, show_match: bool = False):
    """Render a horizontally scrollable Netflix-style row of movie cards."""
    if not movies_list:
        return

    # Build card HTML for every movie in the row
    cards_html = ""
    for idx, movie in enumerate(movies_list):
        movie_id   = movie.get("movie_id") if hasattr(movie, "get") else movie["movie_id"]
        raw_title  = str(movie.get("title") if hasattr(movie, "get") else movie["title"])
        poster, rating, release, _, genres = fetch_movie(movie_id, title=raw_title)
        trailer_url, provider_name, watch_url = get_card_action_links(movie_id, raw_title)
        fallback   = make_fallback_poster_svg(raw_title)
        year       = (release[:4] if release and release != "Unknown" else "N/A")
        genre      = genres.split(",")[0].strip() if genres and genres != "Unknown" else "Movie"
        try:
            rating_val = round(float(rating), 1)
        except Exception:
            rating_val = rating
        r_class    = rating_bucket(rating)
        safe_title = esc(raw_title)
        safe_prov  = esc(provider_name)

        match_html = ""
        if show_match and hasattr(movie, "get") and movie.get("match_score") is not None:
            try:
                sc = int(movie["match_score"])
                match_html = f'<span class="nf-chip match">🎯 {sc}%</span>'
            except Exception:
                pass

        ribbon_html = '<span class="new-ribbon">NEW</span>' if is_new_release(year) else ""

        cards_html += f"""
        <div class="nf-card">
            <div class="nf-card-inner">
                <img class="nf-card-img" src="{poster}" alt="{safe_title}" loading="lazy"
                     onerror="this.onerror=null;this.src='{fallback}';">
                {ribbon_html}
                <span class="rating-badge {r_class}">⭐ {rating_val}</span>
                <div class="nf-card-overlay">
                    <div class="nf-card-title">{safe_title}</div>
                    <div class="nf-card-meta">
                        <span>📅 {year}</span>
                        <span>•</span>
                        <span>🎭 {genre}</span>
                        {match_html}
                    </div>
                    <div class="nf-card-actions">
                        <a href="{trailer_url}" target="_blank" rel="noopener noreferrer"
                           class="nf-btn-trailer" title="Watch Official Trailer">▶ Trailer</a>
                        <a href="{watch_url}" target="_blank" rel="noopener noreferrer"
                           class="nf-btn-watch" title="Watch on {safe_prov}">🍿 Watch</a>
                    </div>
                </div>
            </div>
        </div>
        """

    st.html(f"""
    <div class="nf-row">
        <div class="nf-row-title">{title}</div>
        <div class="nf-row-scroll">
            {cards_html}
        </div>
    </div>
    """)

# -------------------------------------------------
# BRAND HEADER & NAVIGATION
# -------------------------------------------------

render_brand_navbar()

tab_home, tab_search, tab_reco, tab_discover, tab_compare, tab_lists, tab_dash = st.tabs(
    [
        "🏠 Home",
        "🔍 Search",
        "🎯 AI Matches",
        "🔥 Discover",
        "⚔️ Compare",
        "📋 My Lists",
        "📊 Stats",
    ]
)

# ---------------- HOME / FEATURED ----------------
with tab_home:
    hero_top_col1, hero_top_col2 = st.columns([2, 1])
    with hero_top_col1:
        st.markdown("<div style='font-size:13px; font-weight:700; color:#E50914; letter-spacing:1px; text-transform:uppercase; padding-top:8px;'>✨ Featured Spotlight</div>", unsafe_allow_html=True)
    with hero_top_col2:
        if st.button("🎲 Surprise Me", use_container_width=True, key="surprise_main"):
            st.session_state.random_movie = movies.sample(1).iloc[0]
            st.rerun()

    random_movie = st.session_state.random_movie
    poster, rating, release, overview, genres = fetch_movie(random_movie["movie_id"], title=random_movie["title"])
    year = release[:4] if release and release != "Unknown" else "N/A"
    pick_trailer_url, pick_provider, pick_watch_url = get_card_action_links(
        random_movie["movie_id"], random_movie["title"]
    )
    genre_first = genres.split(",")[0].strip() if genres and genres != "Unknown" else "Movie"
    short_overview = overview[:220] + "…" if len(overview) > 220 else overview
    pick_fallback = make_fallback_poster_svg(random_movie["title"])

    # Single Netflix Billboard Hero on Home
    st.html(f"""
    <div class="nf-hero" style="background-image:
        linear-gradient(to right, rgba(20,20,20,0.98) 0%, rgba(20,20,20,0.72) 42%, rgba(20,20,20,0.08) 70%, transparent 100%),
        linear-gradient(to top, rgba(20,20,20,0.95) 0%, transparent 40%),
        url('{poster}');">
        <div class="nf-hero-content">
            <div class="nf-hero-logo">🎬 CINEVERSE SPOTLIGHT</div>
            <h1 class="nf-hero-title">{esc(random_movie["title"])}</h1>
            <div class="nf-hero-meta">
                <span class="nf-hero-rating">⭐ {rating}</span>
                <span class="nf-hero-year">{year}</span>
                <span class="nf-hero-genre">{genre_first}</span>
                <span class="nf-hero-catalog">🍿 {len(movies):,} Films</span>
            </div>
            <p class="nf-hero-overview">{esc(short_overview)}</p>
            <div class="nf-hero-btns">
                <a href="{pick_watch_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-play">▶ Play</a>
                <a href="{pick_trailer_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-info">ℹ Trailer</a>
            </div>
        </div>
    </div>
    """)

    # Actions below hero
    col_fav, col_watch = st.columns(2)
    with col_fav:
        list_button(random_movie["title"], "favorites", "Favorite", "❤️", key="fav_pick")
    with col_watch:
        list_button(random_movie["title"], "watchlist", "Watchlist", "📋", key="watch_pick")

    with st.expander("▶ Watch Trailer Video", expanded=False):
        render_trailer_block(random_movie["movie_id"], random_movie["title"])

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 1. More Like This Spotlight
    if random_movie["title"] in movies["title"].values:
        _pick_recs = recommend(random_movie["title"], top_n=10)
        _pick_movies_list = [row for _, row in _pick_recs.iterrows()]
        render_nf_row("🎯 You Might Also Like", _pick_movies_list, "pick_reco", show_match=True)

    # 2. Trending This Week
    _home_trending = discover_movies("trending")
    if _home_trending:
        _t_rows = [{"movie_id": m.get("id"), "title": m.get("title") or m.get("name") or "Unknown"} for m in _home_trending]
        render_nf_row("🔥 Trending This Week", _t_rows, "home_trending")

    # 3. Top Rated Hits
    _home_top = discover_movies("top_rated")
    if _home_top:
        _top_rows = [{"movie_id": m.get("id"), "title": m.get("title") or m.get("name") or "Unknown"} for m in _home_top]
        render_nf_row("🏆 Critically Acclaimed & Top Rated", _top_rows, "home_top")

    # 4. Because You Liked
    if st.session_state.favorites:
        _sample_fav = st.session_state.favorites[0]
        if _sample_fav in movies["title"].values:
            _fav_recs = recommend(_sample_fav, top_n=10)
            render_nf_row(f"❤️ Because You Liked: {_sample_fav}", [row for _, row in _fav_recs.iterrows()], "home_fav_recs")

# ---------------- SEARCH & DETAILS ----------------
with tab_search:
    st.subheader("🔍 Search Movie")
    selected_movie = st.selectbox(
        "Choose a movie",
        movies["title"].values,
        help="Type to search your favorite movie.",
        key="movie_selector",
    )

    st.session_state.setdefault("last_selected", selected_movie)
    if selected_movie != st.session_state.last_selected:
        st.session_state.last_selected = selected_movie

    selected = movies[movies["title"] == selected_movie].iloc[0]
    poster, rating, release, overview, genres = fetch_movie(selected["movie_id"], title=selected["title"])
    year = release[:4] if release and release != "Unknown" else "N/A"
    sel_trailer_url, sel_provider, sel_watch_url = get_card_action_links(
        selected["movie_id"], selected["title"]
    )
    sel_genre_first = genres.split(",")[0].strip() if genres and genres != "Unknown" else "Movie"
    sel_fallback = make_fallback_poster_svg(selected["title"])
    sel_short_ov = overview[:200] + "…" if len(overview) > 200 else overview

    # Netflix hero for selected movie
    st.html(f"""
    <div class="nf-hero" style="background-image:
        linear-gradient(to right, rgba(20,20,20,0.97) 0%, rgba(20,20,20,0.72) 42%, rgba(20,20,20,0.08) 70%, transparent 100%),
        linear-gradient(to top, rgba(20,20,20,0.92) 0%, transparent 40%),
        url('{poster}');">
        <div class="nf-hero-content">
            <div class="nf-hero-logo">🔍 MOVIE DETAILS</div>
            <h1 class="nf-hero-title">{esc(selected["title"])}</h1>
            <div class="nf-hero-meta">
                <span class="nf-hero-rating">⭐ {rating}</span>
                <span class="nf-hero-year">{year}</span>
                <span class="nf-hero-genre">{sel_genre_first}</span>
            </div>
            <p class="nf-hero-overview">{esc(sel_short_ov)}</p>
            <div class="nf-hero-btns">
                <a href="{sel_watch_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-play">▶ Watch</a>
                <a href="{sel_trailer_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-info">ℹ Trailer</a>
            </div>
        </div>
    </div>
    """)

    # Genre chips + actions below hero
    if genres and genres != "Unknown":
        st.markdown(
            " ".join(f'<span class="genre">{g.strip()}</span>' for g in genres.split(",")),
            unsafe_allow_html=True,
        )

    colA, colB = st.columns(2)
    with colA:
        list_button(selected["title"], "favorites", "Favorite", "❤️", key="fav_detail")
    with colB:
        list_button(selected["title"], "watchlist", "Watchlist", "📋", key="watch_detail")

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    rate_movie(selected["title"], key="rate_detail")

    st.divider()
    st.markdown("### 🎭 Top Cast")
    render_cast_row(get_credits(selected["movie_id"]))

    st.divider()
    st.markdown("### ▶ Trailer")
    render_trailer_block(selected["movie_id"], selected["title"])

    # Similar movies row
    if selected["title"] in movies["title"].values:
        _sim_recs = recommend(selected["title"], top_n=10)
        render_nf_row("🎯 More Like This", [row for _, row in _sim_recs.iterrows()], "search_sim", show_match=True)

# ---------------- RECOMMENDATIONS ----------------
with tab_reco:
    # 1. Improved Header UI
    current_selection = st.session_state.get('last_selected', selected_movie)
    st.html(f"""
    <div style="padding: 12px 0 18px 0; text-align:center;">
        <h2 style="margin-bottom:5px; font-family:'Bebas Neue',sans-serif; font-size:32px; letter-spacing:1px; color:#E50914;">
            🎯 AI Matchmaker
        </h2>
        <p style="color:#BCBCBC; font-size:15px; margin:0;">
            Based on <b style="color:white;">{esc(current_selection)}</b>
        </p>
    </div>
    """)

    ctrl_left, ctrl_right = st.columns([2, 1])
    with ctrl_left:
        num_reco = st.slider("How many recommendations?", min_value=5, max_value=20, value=10, step=5)
    with ctrl_right:
        st.write("")
        st.write("")
        recommend_btn = st.button("🎬 Generate Matches", use_container_width=True)

    if recommend_btn:
        with st.spinner("🤖 AI is analyzing genres, cast, and cinematic themes..."):
            recommendations = recommend(current_selection, top_n=num_reco)

        st.session_state.history.append(
            {"movie": current_selection, "count": num_reco, "time": datetime.now().strftime("%d-%m-%Y %H:%M")}
        )
        st.session_state.last_recommendations = recommendations
        st.success(f"✨ Found top {len(recommendations)} matches!")

    if "last_recommendations" in st.session_state:
        recommendations = st.session_state.last_recommendations
        reco_list = [row for _, row in recommendations.iterrows()]
        # Split into two Netflix rows of up to 10
        render_nf_row(f"🎯 Top Picks Based on {esc(current_selection)}", reco_list[:10], "reco_top", show_match=True)
        if len(reco_list) > 10:
            render_nf_row("🍿 More Matches", reco_list[10:], "reco_more", show_match=True)

# ---------------- DISCOVER ----------------
with tab_discover:

    st.markdown('<div class="nf-section-title">🔥 Discover</div>', unsafe_allow_html=True)

    # Because You Liked rows
    if st.session_state.favorites:
        if "discover_favorite_picks" not in st.session_state:
            pick_count = min(2, len(st.session_state.favorites))
            st.session_state.discover_favorite_picks = (
                pd.Series(st.session_state.favorites).sample(n=pick_count).tolist()
            )

        if st.button("🔄 Shuffle Picks", use_container_width=True, key="shuffle_discover"):
            pick_count = min(2, len(st.session_state.favorites))
            st.session_state.discover_favorite_picks = (
                pd.Series(st.session_state.favorites).sample(n=pick_count).tolist()
            )
            st.rerun()

        for fav_title in st.session_state.discover_favorite_picks:
            if fav_title in movies["title"].values:
                recs = recommend(fav_title, top_n=10)
                render_nf_row(
                    f"❤️ Because You Liked: {fav_title}",
                    [row for _, row in recs.iterrows()],
                    f"because_{fav_title[:12]}"
                )
    else:
        st.info("❤️ Add movies to your Favorites to get personalized recommendations.")

    st.divider()

    # Trending / Top Rated / By Genre
    mode_label = st.radio(
        "Browse",
        ["Trending This Week", "Top Rated", "By Genre"],
        horizontal=True,
        key="discover_mode",
    )

    genre_id = None
    if mode_label == "By Genre":
        genre_map = get_genre_map()
        if genre_map:
            genre_name = st.selectbox("Pick a genre", list(genre_map.keys()), key="discover_genre")
            genre_id = genre_map[genre_name]
        else:
            st.warning("Couldn't load the genre list right now.")

    mode_key = {
        "Trending This Week": "trending",
        "Top Rated": "top_rated",
        "By Genre": "genre"
    }[mode_label]

    if mode_key != "genre" or genre_id:
        with st.spinner("Fetching movies..."):
            results = discover_movies(mode=mode_key, genre_id=genre_id)

        if not results:
            st.info("No results right now.")
        else:
            # Convert raw TMDB dicts so render_nf_row can consume them
            def _tmdb_to_row(m):
                """Wrap a raw TMDB result dict as a dict with 'movie_id' key."""
                m2 = dict(m)
                m2["movie_id"] = m.get("id")
                m2["title"]    = m.get("title") or m.get("name") or "Unknown"
                return m2

            disc_movies = [_tmdb_to_row(m) for m in results]
            row_label = {
                "trending": "🔥 Trending This Week",
                "top_rated": "🏆 Top Rated",
                "genre": f"🎭 {genre_name if genre_id else 'Genre'}"
            }.get(mode_key, mode_label)

            render_nf_row(row_label, disc_movies, mode_key)

# ---------------- COMPARE MOVIES ----------------
with tab_compare:
    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 20px 0;">
            <h2 style="margin-bottom: 5px;">⚔️ Movie Showdown</h2>
            <p style="color: var(--text-muted); font-size: 15px;">
                Compare two films side-by-side to analyze ratings, runtime, genres, and audience reception.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Movie Selection Panel
    sel_col1, vs_col, sel_col2 = st.columns([4, 1, 4])
    
    with sel_col1:
        movie_a_name = st.selectbox(
            "Select First Movie", 
            movies['title'].values, 
            index=0, 
            key="cmp_m1"
        )
    
    with vs_col:
        st.markdown(
            """
            <div style="display:flex; align-items:center; justify-content:center; height:100%; margin-top:12px;">
                <span class="compare-vs-badge">VS</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with sel_col2:
        # Default second movie to second index if available
        default_idx = 1 if len(movies) > 1 else 0
        movie_b_name = st.selectbox(
            "Select Second Movie", 
            movies['title'].values, 
            index=default_idx, 
            key="cmp_m2"
        )

    st.divider()

    # Fetch Data for Both Movies
    movie_a = movies[movies['title'] == movie_a_name].iloc[0]
    movie_b = movies[movies['title'] == movie_b_name].iloc[0]

    post_a, rate_a, rel_a, ov_a, gen_a = fetch_movie(movie_a["movie_id"], title=movie_a_name)
    post_b, rate_b, rel_b, ov_b, gen_b = fetch_movie(movie_b["movie_id"], title=movie_b_name)
    run_a = get_runtime(movie_a["movie_id"])
    run_b = get_runtime(movie_b["movie_id"])

    fall_a = make_fallback_poster_svg(movie_a_name)
    fall_b = make_fallback_poster_svg(movie_b_name)

    trailer_a, prov_a, watch_a = get_card_action_links(movie_a["movie_id"], movie_a_name)
    trailer_b, prov_b, watch_b = get_card_action_links(movie_b["movie_id"], movie_b_name)

    # Safe Float Conversion for Ratings
    try:
        val_rate_a = float(rate_a)
    except (ValueError, TypeError):
        val_rate_a = 0.0

    try:
        val_rate_b = float(rate_b)
    except (ValueError, TypeError):
        val_rate_b = 0.0

    # 2. Side-by-Side Visual Poster Cards
    card_col1, card_col2 = st.columns(2)

    with card_col1:
        winner_a = "🏆 HIGHER RATED" if val_rate_a > val_rate_b else ""
        badge_a_html = f'<div class="compare-winner-pill">{winner_a}</div>' if winner_a else ""
        rel_a_year = rel_a[:4] if rel_a and rel_a != "Unknown" else "N/A"
        
        st.html(
            f"""
            <div class="compare-card">
                {badge_a_html}
                <img src="{post_a}" class="compare-poster" alt="{esc(movie_a_name)}" onerror="this.onerror=null;this.src='{fall_a}';">
                <h3 class="compare-title">{esc(movie_a_name)}</h3>
                <div class="compare-meta">⭐ {rate_a} • 📅 {rel_a_year}</div>
                <div class="card-actions" style="max-width: 240px; margin: 12px auto 0;">
                    <a href="{trailer_a}" target="_blank" rel="noopener noreferrer" class="card-btn btn-trailer">▶ Trailer</a>
                    <a href="{watch_a}" target="_blank" rel="noopener noreferrer" class="card-btn btn-watch" title="Watch on {esc(prov_a)}">🍿 Watch</a>
                </div>
            </div>
            """
        )

    with card_col2:
        winner_b = "🏆 HIGHER RATED" if val_rate_b > val_rate_a else ""
        badge_b_html = f'<div class="compare-winner-pill">{winner_b}</div>' if winner_b else ""
        rel_b_year = rel_b[:4] if rel_b and rel_b != "Unknown" else "N/A"

        st.html(
            f"""
            <div class="compare-card">
                {badge_b_html}
                <img src="{post_b}" class="compare-poster" alt="{esc(movie_b_name)}" onerror="this.onerror=null;this.src='{fall_b}';">
                <h3 class="compare-title">{esc(movie_b_name)}</h3>
                <div class="compare-meta">⭐ {rate_b} • 📅 {rel_b_year}</div>
                <div class="card-actions" style="max-width: 240px; margin: 12px auto 0;">
                    <a href="{trailer_b}" target="_blank" rel="noopener noreferrer" class="card-btn btn-trailer">▶ Trailer</a>
                    <a href="{watch_b}" target="_blank" rel="noopener noreferrer" class="card-btn btn-watch" title="Watch on {esc(prov_b)}">🍿 Watch</a>
                </div>
            </div>
            """
        )

    st.write("")

    # 3. Head-to-Head Detailed Comparison Table
    st.markdown("### 📊 Head-to-Head Metrics")

    m_col1, m_col2, m_col3 = st.columns([3, 2, 3])

    with m_col1:
        st.metric("Rating", f"⭐ {rate_a}", delta=f"{round(val_rate_a - val_rate_b, 1)}" if val_rate_a != val_rate_b else "Tied")
        st.markdown(f"**Runtime:** {run_a if run_a else 'N/A'} mins")
        st.markdown(f"**Genres:** {gen_a if gen_a else 'N/A'}")

    with m_col2:
        st.markdown(
            """
            <div style="text-align: center; color: var(--text-muted); font-size: 13px; padding-top: 10px;">
                <p><b>Rating Difference</b></p>
                <p style="font-size: 22px; color: #FFC94A;">⚡</p>
                <p><b>Shared Vibe</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col3:
        st.metric("Rating", f"⭐ {rate_b}", delta=f"{round(val_rate_b - val_rate_a, 1)}" if val_rate_b != val_rate_a else "Tied")
        st.markdown(f"**Runtime:** {run_b if run_b else 'N/A'} mins")
        st.markdown(f"**Genres:** {gen_b if gen_b else 'N/A'}")

    st.divider()

    # 4. Overview & Synopsis Comparison
    st.markdown("### 📖 Synopsis Comparison")
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.info(f"**{movie_a_name}**\n\n{movie_a.get('overview', 'No overview available.')}")
    with exp_col2:
        st.info(f"**{movie_b_name}**\n\n{movie_b.get('overview', 'No overview available.')}")

# ---------------- MY LISTS ----------------
with tab_lists:
    st.markdown("<h2 style='text-align:center'>📋 My Collections</h2>", unsafe_allow_html=True)
    
    # Sub-tabs to keep the UI clean instead of endless scrolling
    list_tabs = st.tabs(["❤️ Favorites", "🎬 Watchlist", "⭐ My Ratings", "⚙️ Manage & Export"])
    
    # Helper function to render a list of titles as a Netflix carousel row
    def render_movie_grid(movie_titles, key_prefix, section_title=""):
        if not movie_titles:
            st.info("Nothing here yet. Start exploring and add some movies!")
            return
            
        # Match titles from session state back to the main dataframe
        matched_movies = movies[movies['title'].isin(movie_titles)]
        movie_list = [row for _, row in matched_movies.iterrows()]
        render_nf_row(section_title or "Saved Movies", movie_list, key_prefix)

    with list_tabs[0]:
        render_movie_grid(st.session_state.favorites, "list_fav", "❤️ Your Favorites")
        
    with list_tabs[1]:
        render_movie_grid(st.session_state.watchlist, "list_watch", "🎬 Your Watchlist")
        
    with list_tabs[2]:
        if not st.session_state.ratings:
            st.info("⭐ You haven't rated anything yet. Rate movies from the Search & Details tab.")
        else:
            rated_titles = list(st.session_state.ratings.keys())
            rated_movies = movies[movies['title'].isin(rated_titles)]
            render_nf_row("⭐ Rated by You", [row for _, row in rated_movies.iterrows()], "list_rated")

    with list_tabs[3]:
        st.subheader("📤 Export Data")
        exp1, exp2 = st.columns(2)
        with exp1:
            fav_csv = pd.DataFrame({"title": st.session_state.favorites}).to_csv(index=False).encode("utf-8")
            st.download_button(
                "📤 Export Favorites (CSV)", fav_csv, file_name="favorites.csv", mime="text/csv",
                use_container_width=True, disabled=not st.session_state.favorites,
            )
        with exp2:
            watch_csv = pd.DataFrame({"title": st.session_state.watchlist}).to_csv(index=False).encode("utf-8")
            st.download_button(
                "📤 Export Watchlist (CSV)", watch_csv, file_name="watchlist.csv", mime="text/csv",
                use_container_width=True, disabled=not st.session_state.watchlist,
            )

        st.divider()
        st.subheader("⚡ Quick Actions")
        a, b, c, d = st.columns(4)
        with a:
            if st.button("🧹 Clear Favorites", use_container_width=True):
                st.session_state.favorites = []
                save_user_data()
                st.toast("Favorites Cleared", icon="🧹")
                st.rerun()
        with b:
            if st.button("🗑 Clear Watchlist", use_container_width=True):
                st.session_state.watchlist = []
                save_user_data()
                st.toast("Watchlist Cleared", icon="🗑")
                st.rerun()
        with c:
            if st.button("♻ Reset History", use_container_width=True):
                st.session_state.history = []
                save_user_data()
                st.toast("History Cleared", icon="♻")
                st.rerun()
        with d:
            if st.button("⭐ Reset Ratings", use_container_width=True):
                st.session_state.ratings = {}
                save_user_data()
                st.toast("Ratings Cleared", icon="⭐")
                st.rerun()

# ---------------- DASHBOARD ----------------
with tab_dash:
    st.header("📊 Dashboard")
    st.caption("Your CineVerse activity at a glance")

    # ---- stat cards ----
    avg_rating = (
        round(sum(st.session_state.ratings.values()) / len(st.session_state.ratings), 1)
        if st.session_state.ratings else "–"
    )
    stats = [
        ("🎞️", len(movies), "Catalog"),
        ("❤️", len(st.session_state.favorites), "Favorites"),
        ("📋", len(st.session_state.watchlist), "Watchlist"),
        ("🔍", len(st.session_state.history), "Searches Run"),
        ("⭐", avg_rating, "Avg. Your Rating"),
    ]
    stat_html = '<div class="dash-stat-row">' + "".join(
        f"""<div class="dash-stat-card" style="animation-delay:{i * 0.05}s">
                <span class="dash-stat-icon">{icon}</span>
                <div class="dash-stat-value">{value}</div>
                <div class="dash-stat-label">{label}</div>
            </div>"""
        for i, (icon, value, label) in enumerate(stats)
    ) + "</div>"
    st.markdown(stat_html, unsafe_allow_html=True)

    st.divider()

    # ---- genre taste profile + engagement ----
    col_donut, col_eng = st.columns([1.15, 1])

    with col_donut:
        st.markdown('<div class="dash-section-title">🎭 Genre Taste Profile</div>', unsafe_allow_html=True)
        tracked_titles = list(dict.fromkeys(st.session_state.favorites + st.session_state.watchlist))

        if not tracked_titles:
            st.info("Add movies to Favorites or your Watchlist to build your genre taste profile.")
        else:
            genre_counts = {}
            for t in tracked_titles:
                match = movies[movies["title"] == t]
                if match.empty:
                    continue
                _, _, _, _, genres_str = fetch_movie(match.iloc[0]["movie_id"], title=t)
                primary = genres_str.split(",")[0].strip() if genres_str and genres_str != "Unknown" else "Other"
                genre_counts[primary] = genre_counts.get(primary, 0) + 1

            palette = ["#E50914", "#FFC94A", "#3ddc84", "#5b8def", "#b06fe0", "#8b93a3"]
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:6]
            total = sum(c for _, c in top_genres) or 1

            slices, legend_rows, cursor = [], [], 0.0
            for i, (name, count) in enumerate(top_genres):
                pct = (count / total) * 100
                color = palette[i % len(palette)]
                slices.append(f"{color} {cursor:.2f}% {cursor + pct:.2f}%")
                cursor += pct
                legend_rows.append(
                    f'<div class="donut-legend-row"><span class="donut-dot" '
                    f'style="background:{color}"></span>{esc(name)}'
                    f'<span class="donut-legend-count">{count}</span></div>'
                )

            donut_html = f"""
            <div class="donut-wrap">
                <div class="donut" style="--donut-slices:{','.join(slices)}">
                    <div class="donut-hole">
                        <div class="dh-value">{total}</div>
                        <div class="dh-label">Tracked</div>
                    </div>
                </div>
                <div class="donut-legend">{''.join(legend_rows)}</div>
            </div>
            """
            st.markdown(donut_html, unsafe_allow_html=True)

    with col_eng:
        st.markdown('<div class="dash-section-title">📈 Engagement</div>', unsafe_allow_html=True)
        catalog_size = max(len(movies), 1)
        bars = [
            ("Favorited", len(st.session_state.favorites), "linear-gradient(90deg,#E50914,#FF3B4E)"),
            ("Watchlisted", len(st.session_state.watchlist), "linear-gradient(90deg,#FFC94A,#FFA726)"),
            ("Rated", len(st.session_state.ratings), "linear-gradient(90deg,#3ddc84,#1fae66)"),
        ]
        bar_html = ""
        for label, count, gradient in bars:
            pct = min(100, round((count / catalog_size) * 100, 2))
            bar_html += f"""
            <div class="eng-bar-row">
                <div class="eng-bar-top"><span>{label}</span><b>{count} movies</b></div>
                <div class="eng-bar-track">
                    <div class="eng-bar-fill" style="width:{pct}%; background:{gradient}"></div>
                </div>
            </div>
            """
        st.markdown(bar_html, unsafe_allow_html=True)
        st.caption("Share of the full catalog you've engaged with.")

    st.divider()

    # ---- highlight callouts ----
    st.markdown('<div class="dash-section-title">🏆 Highlights</div>', unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)

    with h1:
        if st.session_state.favorites:
            top_fav = st.session_state.favorites[-1]
            st.markdown(
                f'<div class="dash-highlight"><div class="dh-tag">Latest Favorite</div>'
                f'<div class="dh-title">❤️ {esc(top_fav)}</div>'
                f'<div class="dh-sub">Added to your favorites</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="dash-highlight"><div class="dh-tag">Latest Favorite</div>'
                '<div class="dh-sub">None yet — go heart a movie!</div></div>',
                unsafe_allow_html=True,
            )

    with h2:
        if st.session_state.ratings:
            best_title, best_score = max(st.session_state.ratings.items(), key=lambda x: x[1])
            st.markdown(
                f'<div class="dash-highlight"><div class="dh-tag">Top Rated By You</div>'
                f'<div class="dh-title">⭐ {esc(best_title)}</div>'
                f'<div class="dh-sub">{"⭐" * best_score}{"☆" * (5 - best_score)}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="dash-highlight"><div class="dh-tag">Top Rated By You</div>'
                '<div class="dh-sub">Rate a movie to see it here.</div></div>',
                unsafe_allow_html=True,
            )

    with h3:
        if st.session_state.history:
            counts = {}
            for h in st.session_state.history:
                counts[h["movie"]] = counts.get(h["movie"], 0) + 1
            most_movie, most_n = max(counts.items(), key=lambda x: x[1])
            st.markdown(
                f'<div class="dash-highlight"><div class="dh-tag">Most Searched</div>'
                f'<div class="dh-title">🔍 {esc(most_movie)}</div>'
                f'<div class="dh-sub">Used as base {most_n}× for recommendations</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="dash-highlight"><div class="dh-tag">Most Searched</div>'
                '<div class="dh-sub">Generate a recommendation to see it here.</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ---- recent activity feed ----
    st.markdown('<div class="dash-section-title">🕒 Recent Activity</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("🕒 No recommendation history yet — generate some AI recommendations to populate this feed.")
    else:
        recent = list(reversed(st.session_state.history))[:8]
        rows = "".join(
            f"""<div class="activity-row" style="animation-delay:{i * 0.04}s">
                    <div class="activity-icon">🎯</div>
                    <div class="activity-main">
                        <div class="activity-title">{esc(h['movie'])}</div>
                        <div class="activity-sub">{h['count']} recommendations generated</div>
                    </div>
                    <div class="activity-sub">{esc(h['time'])}</div>
                </div>"""
            for i, h in enumerate(recent)
        )
        st.markdown(f'<div class="activity-feed">{rows}</div>', unsafe_allow_html=True)

        with st.expander("📄 View full history table"):
            history_df = pd.DataFrame(st.session_state.history)
            st.dataframe(history_df, use_container_width=True, hide_index=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown("---")
st.markdown(
    """
    <div class='footer'>
        <h3>🎬 CineVerse AI</h3>
        AI Powered Movie Recommendation System
        <br>
        Developed by <b>Amit Akhade</b>
        <br>
        Final Year Project • 2026
    </div>
    """,
    unsafe_allow_html=True,
)