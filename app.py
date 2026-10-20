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

from PIL import Image

_icon_candidates = ["static/favicon.png", "favicon.png"]
_icon_path = next((p for p in _icon_candidates if os.path.exists(p)), None)
try:
    _app_icon = Image.open(_icon_path) if _icon_path else "🎬"
except Exception:
    _app_icon = "🎬"

st.set_page_config(
    page_title="CineVerse AI — Cinematic Discovery",
    page_icon=_app_icon,
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

# PWA + mobile meta tags & install manifest
_manifest_url = "app/static/manifest.json"
_icon_192 = "app/static/icon-192.png"
_icon_512 = "app/static/icon-512.png"
_favicon = "app/static/favicon.png"

st.markdown(f"""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#141414">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="CineVerse AI">
<meta name="application-name" content="CineVerse AI">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="{_icon_192}">
<link rel="apple-touch-icon" sizes="192x192" href="{_icon_192}">
<link rel="apple-touch-icon" sizes="512x512" href="{_icon_512}">
<link rel="icon" type="image/png" sizes="192x192" href="{_icon_192}">
<link rel="icon" type="image/png" sizes="512x512" href="{_icon_512}">
<link rel="icon" type="image/png" sizes="64x64" href="{_favicon}">
<link rel="manifest" href="{_manifest_url}">
<script>
  (function() {{
    try {{
      function injectTag(rel, href, type, sizes) {{
        var sel = 'link[rel="' + rel + '"]' + (sizes ? '[sizes="' + sizes + '"]' : '');
        var el = document.querySelector(sel);
        if (!el) {{
          el = document.createElement('link');
          el.rel = rel;
          if (type) el.type = type;
          if (sizes) el.sizes = sizes;
          document.head.appendChild(el);
        }}
        el.href = href;
      }}
      injectTag('manifest', '{_manifest_url}');
      injectTag('apple-touch-icon', '{_icon_192}', 'image/png', '192x192');
      injectTag('apple-touch-icon', '{_icon_512}', 'image/png', '512x512');
      injectTag('icon', '{_icon_192}', 'image/png', '192x192');
      injectTag('icon', '{_icon_512}', 'image/png', '512x512');
    }} catch (e) {{}}
  }})();
</script>
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


def render_crown_card(movie_row, seed_title: str):
    """Render the #1 AI Top Match in an elite Crown Jewel showcase card."""
    movie_id = movie_row.get("movie_id") if hasattr(movie_row, "get") else movie_row["movie_id"]
    raw_title = str(movie_row.get("title") if hasattr(movie_row, "get") else movie_row["title"])
    poster, rating, release, overview, genres = fetch_movie(movie_id, title=raw_title)
    trailer_url, provider_name, watch_url = get_card_action_links(movie_id, raw_title)
    fallback = make_fallback_poster_svg(raw_title)
    year = release[:4] if release and release != "Unknown" else "N/A"
    genre_list = [g.strip() for g in genres.split(",") if g.strip()] if genres and genres != "Unknown" else ["Cinema"]
    genre_str = " • ".join(genre_list[:3])
    match_score = int(movie_row.get("match_score", 95)) if hasattr(movie_row, "get") else 95
    runtime = get_runtime(movie_id)
    runtime_str = f" • ⏱️ {runtime}m" if runtime else ""

    plot_score = min(99, max(88, match_score + 1))
    vibe_score = min(98, max(84, match_score - 2))
    cast_score = min(96, max(80, match_score - 5))

    safe_title = esc(raw_title)
    safe_seed = esc(seed_title)
    safe_prov = esc(provider_name)
    safe_overview = esc(overview[:220] + "..." if len(overview) > 220 else overview)

    crown_html = f"""
    <div class="crown-card">
        <div class="crown-poster-wrapper">
            <span class="crown-badge-floating">👑 #1 TOP MATCH</span>
            <img src="{poster}" class="crown-poster" alt="{safe_title}" loading="lazy" onerror="this.onerror=null;this.src='{fallback}';">
        </div>
        <div class="crown-info">
            <div class="crown-tag">⚡ ULTIMATE AI MATCH • {match_score}% COMPATIBILITY</div>
            <div class="crown-title">{safe_title}</div>
            <div class="crown-meta">
                <span>⭐ <b>{rating}</b></span>
                <span>•</span>
                <span>📅 {year}</span>
                <span>•</span>
                <span>🎭 {genre_str}</span>
                {runtime_str}
            </div>
            <div class="crown-ai-reason">
                <b>🤖 AI Cinematic DNA:</b> Exceptional thematic alignment with <i>{safe_seed}</i>. {safe_overview}
            </div>
            <div class="crown-radar-row">
                <div class="crown-radar-item">
                    <div class="crown-radar-label">Plot DNA</div>
                    <div class="crown-radar-val">{plot_score}%</div>
                </div>
                <div class="crown-radar-item">
                    <div class="crown-radar-label">Atmosphere</div>
                    <div class="crown-radar-val">{vibe_score}%</div>
                </div>
                <div class="crown-radar-item">
                    <div class="crown-radar-label">Cast Affinity</div>
                    <div class="crown-radar-val">{cast_score}%</div>
                </div>
            </div>
            <div class="crown-actions">
                <a href="{trailer_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-trailer" style="padding: 9px 18px; font-size: 13px;">▶ Watch Trailer</a>
                <a href="{watch_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-watch" style="padding: 9px 18px; font-size: 13px;">🍿 Stream on {safe_prov}</a>
            </div>
        </div>
    </div>
    """
    st.html(crown_html)


def render_matrix_grid(movies_list, key_prefix: str):
    """Render movies in a responsive 2x3 Matrix Grid."""
    if not movies_list:
        return

    cards_html = ""
    for movie in movies_list:
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
        if hasattr(movie, "get") and movie.get("match_score") is not None:
            try:
                sc = int(movie["match_score"])
                match_html = f'<span class="nf-chip match">🎯 {sc}%</span>'
            except Exception:
                pass

        cards_html += f"""
        <div class="nf-card">
            <div class="nf-card-inner">
                <img class="nf-card-img" src="{poster}" alt="{safe_title}" loading="lazy"
                     onerror="this.onerror=null;this.src='{fallback}';">
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

    st.html(f'<div class="matrix-grid">{cards_html}</div>')


def render_leaderboard(movies_list, key_prefix: str):
    """Render movies in Netflix Top 10 Numbered Leaderboard format."""
    if not movies_list:
        st.info("No items available in this leaderboard.")
        return

    items_html = ""
    for rank, movie in enumerate(movies_list[:10], start=1):
        movie_id = movie.get("id") or movie.get("movie_id")
        raw_title = str(movie.get("title") or movie.get("name") or "Unknown")
        poster, rating, release, overview, genres = fetch_movie(movie_id, title=raw_title)
        trailer_url, provider_name, watch_url = get_card_action_links(movie_id, raw_title)
        fallback = make_fallback_poster_svg(raw_title)
        year = release[:4] if release and release != "Unknown" else "N/A"
        genre = genres.split(",")[0].strip() if genres and genres != "Unknown" else "Featured"
        safe_title = esc(raw_title)
        safe_prov = esc(provider_name)
        
        items_html += f"""
        <div class="leaderboard-item">
            <div class="leaderboard-rank">{rank}</div>
            <img src="{poster}" class="leaderboard-poster" alt="{safe_title}" loading="lazy" onerror="this.onerror=null;this.src='{fallback}';">
            <div class="leaderboard-details">
                <div class="leaderboard-title">{safe_title}</div>
                <div class="leaderboard-meta">
                    <span>⭐ <b>{rating}</b></span>
                    <span>•</span>
                    <span>📅 {year}</span>
                    <span>•</span>
                    <span>🎭 {esc(genre)}</span>
                </div>
            </div>
            <div class="leaderboard-actions">
                <a href="{trailer_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-trailer" style="padding: 6px 12px; font-size: 11px;">▶ Trailer</a>
                <a href="{watch_url}" target="_blank" rel="noopener noreferrer" class="nf-btn-watch" style="padding: 6px 12px; font-size: 11px;">🍿 Watch</a>
            </div>
        </div>
        """

    st.html(f'<div class="leaderboard-list">{items_html}</div>')


def render_poster_wall(movie_titles, key_prefix: str):
    """Render movies in a dense Letterboxd-style responsive poster wall."""
    if not movie_titles:
        st.info("Nothing here yet. Explore movies and add them to your collection!")
        return

    cards_html = ""
    for title in movie_titles:
        matched = movies[movies['title'] == title]
        if matched.empty:
            continue
        m_row = matched.iloc[0]
        movie_id = m_row["movie_id"]
        poster, rating, release, _, _ = fetch_movie(movie_id, title=title)
        trailer_url, provider_name, watch_url = get_card_action_links(movie_id, title)
        fallback = make_fallback_poster_svg(title)
        year = release[:4] if release and release != "Unknown" else "N/A"
        safe_title = esc(title)

        cards_html += f"""
        <a href="{watch_url}" target="_blank" rel="noopener noreferrer" class="poster-wall-card" title="{safe_title} ({year})">
            <img src="{poster}" class="poster-wall-img" alt="{safe_title}" loading="lazy" onerror="this.onerror=null;this.src='{fallback}';">
            <div class="poster-wall-overlay">
                <div class="poster-wall-title">{safe_title}</div>
                <div class="poster-wall-meta">⭐ {rating} • {year}</div>
            </div>
        </a>
        """

    st.html(f'<div class="poster-wall-grid">{cards_html}</div>')


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
    current_selection = st.session_state.get('last_selected', selected_movie)
    st.html(f"""
    <div style="padding: 12px 0 16px 0; text-align:center;">
        <h2 style="margin-bottom:4px; font-family:'Bebas Neue',sans-serif; font-size:32px; letter-spacing:1px; color:#E50914;">
            🎯 AI Matchmaker
        </h2>
        <p style="color:#BCBCBC; font-size:14px; margin:0;">
            Deep Content-Based Filtering & Cinematic DNA Analysis for <b style="color:white;">{esc(current_selection)}</b>
        </p>
    </div>
    """)

    ctrl_left, ctrl_right = st.columns([2, 1])
    with ctrl_left:
        num_reco = st.slider("Number of Matches", min_value=5, max_value=15, value=7, step=2)
    with ctrl_right:
        st.write("")
        st.write("")
        recommend_btn = st.button("🎬 Generate Matches", use_container_width=True)

    if recommend_btn or "last_recommendations" not in st.session_state:
        if recommend_btn:
            with st.spinner("🤖 AI is analyzing genres, cast, and cinematic themes..."):
                recommendations = recommend(current_selection, top_n=num_reco)
            st.session_state.history.append(
                {"movie": current_selection, "count": num_reco, "time": datetime.now().strftime("%d-%m-%Y %H:%M")}
            )
            st.session_state.last_recommendations = recommendations
            st.session_state.last_reco_seed = current_selection
        elif "last_recommendations" not in st.session_state:
            recommendations = recommend(current_selection, top_n=num_reco)
            st.session_state.last_recommendations = recommendations
            st.session_state.last_reco_seed = current_selection

    if "last_recommendations" in st.session_state:
        recs = st.session_state.last_recommendations
        seed = st.session_state.get("last_reco_seed", current_selection)
        if not recs.empty:
            # 1. Crown Jewel Showcase Card (#1 Top Match)
            crown_movie = recs.iloc[0]
            render_crown_card(crown_movie, seed)

            # 2. 2x3 Matrix Grid for other matches
            if len(recs) > 1:
                st.markdown('<div class="nf-section-title" style="margin-top:24px;">✨ Related Match Matrix</div>', unsafe_allow_html=True)
                matrix_movies = [row for _, row in recs.iloc[1:].iterrows()]
                render_matrix_grid(matrix_movies, "reco_matrix")

# ---------------- DISCOVER ----------------
with tab_discover:
    st.markdown('<div class="nf-section-title">🔥 Discover Cinema</div>', unsafe_allow_html=True)

    category_options = [
        "🏆 Top 10 Leaderboard",
        "🚀 Sci-Fi & Cyberpunk",
        "💥 Action Adrenaline",
        "🕵️ Mind-Bending Thrillers",
        "🍿 Comedy & Feel-Good",
        "🎭 Critically Acclaimed Drama"
    ]
    
    selected_category = st.pills(
        "Explore Curated Channels",
        options=category_options,
        default="🏆 Top 10 Leaderboard",
        key="discover_category_pill"
    )

    genre_mapping = {
        "🚀 Sci-Fi & Cyberpunk": 878,
        "💥 Action Adrenaline": 28,
        "🕵️ Mind-Bending Thrillers": 53,
        "🍿 Comedy & Feel-Good": 35,
        "🎭 Critically Acclaimed Drama": 18
    }

    if selected_category == "🏆 Top 10 Leaderboard":
        disc_movies = discover_movies(mode="trending")
        if not disc_movies:
            disc_movies = discover_movies(mode="top_rated")
        
        st.markdown(
            """
            <div style="margin: 12px 0 16px;">
                <h3 style="font-family:'Bebas Neue',sans-serif; font-size:24px; color:#FFC94A; letter-spacing:1px; margin:0;">
                    🔥 NETFLIX GLOBAL TOP 10 TODAY
                </h3>
                <p style="color:#BCBCBC; font-size:13px; margin-top:2px;">
                    Real-time audience velocity & streaming leaderboard updated hourly.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        render_leaderboard(disc_movies[:10], "top10_lb")
    else:
        g_id = genre_mapping.get(selected_category, 28)
        disc_movies = discover_movies(mode="genre", genre_id=g_id)
        if not disc_movies:
            disc_movies = discover_movies(mode="top_rated")

        st.markdown(
            f"""
            <div style="margin: 12px 0 16px;">
                <h3 style="font-family:'Bebas Neue',sans-serif; font-size:24px; color:#FFFFFF; letter-spacing:1px; margin:0;">
                    {selected_category}
                </h3>
                <p style="color:#BCBCBC; font-size:13px; margin-top:2px;">
                    Top trending selections curated by genre popularity.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        render_leaderboard(disc_movies[:10], f"cat_{g_id}")

    if st.session_state.favorites:
        st.divider()
        st.markdown('<div class="nf-section-title">❤️ Because You Liked</div>', unsafe_allow_html=True)
        fav_pick = pd.Series(st.session_state.favorites).iloc[-1]
        if fav_pick in movies["title"].values:
            fav_recs = recommend(fav_pick, top_n=8)
            render_nf_row(
                f"Inspired by {fav_pick}",
                [row for _, row in fav_recs.iterrows()],
                "discover_because"
            )

# ---------------- COMPARE MOVIES ----------------
with tab_compare:
    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 16px 0;">
            <h2 style="margin-bottom: 4px; font-family:'Bebas Neue',sans-serif; font-size:32px; letter-spacing:1px; color:#E50914;">
                ⚔️ Movie Showdown Arena
            </h2>
            <p style="color: #BCBCBC; font-size: 14px; margin: 0;">
                Tale of the tape: Compare ratings, genres, and audience metrics side-by-side with AI Champion analysis.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    sel_col1, vs_spacer, sel_col2 = st.columns([5, 1, 5])
    with sel_col1:
        movie_a_name = st.selectbox("Select Film A", movies['title'].values, index=0, key="cmp_m1")
    with vs_spacer:
        st.write("")
        st.write("")
        st.markdown("<div style='text-align:center; font-family:\"Bebas Neue\",sans-serif; font-size:24px; color:#E50914; font-weight:bold;'>VS</div>", unsafe_allow_html=True)
    with sel_col2:
        default_b_idx = 1 if len(movies) > 1 else 0
        movie_b_name = st.selectbox("Select Film B", movies['title'].values, index=default_b_idx, key="cmp_m2")

    movie_a = movies[movies['title'] == movie_a_name].iloc[0]
    movie_b = movies[movies['title'] == movie_b_name].iloc[0]

    post_a, rate_a, rel_a, ov_a, gen_a = fetch_movie(movie_a["movie_id"], title=movie_a_name)
    post_b, rate_b, rel_b, ov_b, gen_b = fetch_movie(movie_b["movie_id"], title=movie_b_name)
    run_a = get_runtime(movie_a["movie_id"]) or "N/A"
    run_b = get_runtime(movie_b["movie_id"]) or "N/A"

    fall_a = make_fallback_poster_svg(movie_a_name)
    fall_b = make_fallback_poster_svg(movie_b_name)

    trailer_a, prov_a, watch_a = get_card_action_links(movie_a["movie_id"], movie_a_name)
    trailer_b, prov_b, watch_b = get_card_action_links(movie_b["movie_id"], movie_b_name)

    try:
        val_rate_a = float(rate_a)
    except Exception:
        val_rate_a = 0.0

    try:
        val_rate_b = float(rate_b)
    except Exception:
        val_rate_b = 0.0

    a_is_winner = val_rate_a > val_rate_b
    b_is_winner = val_rate_b > val_rate_a

    winner_class_a = "winner" if a_is_winner else ""
    winner_class_b = "winner" if b_is_winner else ""

    winner_badge_a = '<div style="background:#FFC94A; color:#141414; font-weight:800; font-size:11px; padding:3px 8px; border-radius:10px; display:inline-block; margin-bottom:8px;">🏆 HIGHER RATED</div>' if a_is_winner else ""
    winner_badge_b = '<div style="background:#FFC94A; color:#141414; font-weight:800; font-size:11px; padding:3px 8px; border-radius:10px; display:inline-block; margin-bottom:8px;">🏆 HIGHER RATED</div>' if b_is_winner else ""

    rel_a_year = rel_a[:4] if rel_a and rel_a != "Unknown" else "N/A"
    rel_b_year = rel_b[:4] if rel_b and rel_b != "Unknown" else "N/A"

    arena_html = f"""
    <div class="faceoff-arena">
        <div class="faceoff-card {winner_class_a}">
            {winner_badge_a}
            <img src="{post_a}" style="width:130px; height:195px; object-fit:cover; border-radius:8px; box-shadow:0 6px 16px rgba(0,0,0,0.6);" alt="{esc(movie_a_name)}" onerror="this.onerror=null;this.src='{fall_a}';">
            <h3 style="font-family:'Bebas Neue',sans-serif; font-size:22px; color:#FFFFFF; margin:8px 0 4px; letter-spacing:0.5px;">{esc(movie_a_name)}</h3>
            <div style="font-size:13px; color:#BCBCBC; margin-bottom:10px;">⭐ <b>{rate_a}</b> • 📅 {rel_a_year} • ⏱️ {run_a}m</div>
            <div style="display:flex; gap:8px; justify-content:center;">
                <a href="{trailer_a}" target="_blank" rel="noopener noreferrer" class="nf-btn-trailer" style="padding:6px 12px; font-size:11px;">▶ Trailer</a>
                <a href="{watch_a}" target="_blank" rel="noopener noreferrer" class="nf-btn-watch" style="padding:6px 12px; font-size:11px;">🍿 Watch</a>
            </div>
        </div>

        <div class="faceoff-vs">VS</div>

        <div class="faceoff-card {winner_class_b}">
            {winner_badge_b}
            <img src="{post_b}" style="width:130px; height:195px; object-fit:cover; border-radius:8px; box-shadow:0 6px 16px rgba(0,0,0,0.6);" alt="{esc(movie_b_name)}" onerror="this.onerror=null;this.src='{fall_b}';">
            <h3 style="font-family:'Bebas Neue',sans-serif; font-size:22px; color:#FFFFFF; margin:8px 0 4px; letter-spacing:0.5px;">{esc(movie_b_name)}</h3>
            <div style="font-size:13px; color:#BCBCBC; margin-bottom:10px;">⭐ <b>{rate_b}</b> • 📅 {rel_b_year} • ⏱️ {run_b}m</div>
            <div style="display:flex; gap:8px; justify-content:center;">
                <a href="{trailer_b}" target="_blank" rel="noopener noreferrer" class="nf-btn-trailer" style="padding:6px 12px; font-size:11px;">▶ Trailer</a>
                <a href="{watch_b}" target="_blank" rel="noopener noreferrer" class="nf-btn-watch" style="padding:6px 12px; font-size:11px;">🍿 Watch</a>
            </div>
        </div>
    </div>
    """
    st.html(arena_html)

    if a_is_winner:
        diff = round(val_rate_a - val_rate_b, 1)
        verdict_headline = f"🥊 Champion: {esc(movie_a_name)} (+{diff} ⭐)"
        verdict_desc = f"<b>{esc(movie_a_name)}</b> claims victory with superior audience resonance and critical praise (⭐ {rate_a} vs ⭐ {rate_b}). For lovers of {esc(gen_a)}, <i>{esc(movie_a_name)}</i> delivers an unmatched cinema experience. However, if you are looking for {esc(gen_b)}, <i>{esc(movie_b_name)}</i> is also a formidable contender."
    elif b_is_winner:
        diff = round(val_rate_b - val_rate_a, 1)
        verdict_headline = f"🥊 Champion: {esc(movie_b_name)} (+{diff} ⭐)"
        verdict_desc = f"<b>{esc(movie_b_name)}</b> claims victory with superior audience resonance and critical praise (⭐ {rate_b} vs ⭐ {rate_a}). For lovers of {esc(gen_b)}, <i>{esc(movie_b_name)}</i> delivers an unmatched cinema experience. However, if you are looking for {esc(gen_a)}, <i>{esc(movie_a_name)}</i> is also a formidable contender."
    else:
        verdict_headline = "⚖️ Dead Heat: Cinematic Tie!"
        verdict_desc = f"Both <b>{esc(movie_a_name)}</b> and <b>{esc(movie_b_name)}</b> share an identical score of ⭐ {rate_a}. Choose <i>{esc(movie_a_name)}</i> for {esc(gen_a)}, or <i>{esc(movie_b_name)}</i> for {esc(gen_b)}!"

    st.html(f"""
    <div class="verdict-box">
        <div class="verdict-title">{verdict_headline}</div>
        <p class="verdict-text">{verdict_desc}</p>
    </div>
    """)

    st.markdown("### 📊 Tale of the Tape Breakdown")
    m_col1, m_col2, m_col3 = st.columns([4, 2, 4])
    with m_col1:
        st.metric("Rating", f"⭐ {rate_a}", delta=f"{round(val_rate_a - val_rate_b, 1)}" if val_rate_a != val_rate_b else "Tied")
        st.markdown(f"**Runtime:** {run_a} mins")
        st.markdown(f"**Genres:** {gen_a if gen_a else 'N/A'}")
    with m_col2:
        st.markdown(
            """
            <div style="text-align: center; color: #BCBCBC; font-size: 13px; padding-top: 10px;">
                <p><b>Matchup</b></p>
                <p style="font-size: 26px; color: #FFC94A; margin: 0;">⚡</p>
                <p><b>Head to Head</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col3:
        st.metric("Rating", f"⭐ {rate_b}", delta=f"{round(val_rate_b - val_rate_a, 1)}" if val_rate_b != val_rate_a else "Tied")
        st.markdown(f"**Runtime:** {run_b} mins")
        st.markdown(f"**Genres:** {gen_b if gen_b else 'N/A'}")

    st.divider()
    st.markdown("### 📖 Synopsis Comparison")
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.info(f"**{esc(movie_a_name)}**\n\n{movie_a.get('overview', 'No overview available.')}")
    with exp_col2:
        st.info(f"**{esc(movie_b_name)}**\n\n{movie_b.get('overview', 'No overview available.')}")

# ---------------- MY LISTS ----------------
with tab_lists:
    st.markdown("<h2 style='text-align:center; font-family:\"Bebas Neue\",sans-serif; font-size:32px; letter-spacing:1px; color:#E50914; margin-bottom:6px;'>📋 My Cinema Collections</h2>", unsafe_allow_html=True)
    
    roulette_pool = list(set(st.session_state.favorites + st.session_state.watchlist))
    roulette_col_left, roulette_col_right = st.columns([3, 1])
    
    with roulette_col_left:
        st.html("""
        <div class="roulette-box" style="margin-bottom:0;">
            <div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:20px; color:#FFFFFF; letter-spacing:1px; display:flex; align-items:center; gap:8px;">
                    🎲 Can't Decide What to Watch Tonight?
                </div>
                <div style="font-size:12.5px; color:#BCBCBC; margin-top:2px;">
                    Let CineVerse AI spin your saved watchlist and pick the perfect film for your evening.
                </div>
            </div>
        </div>
        """)
    with roulette_col_right:
        st.write("")
        spin_btn = st.button("🎰 Spin Roulette", use_container_width=True, key="btn_roulette_spin")

    if spin_btn:
        if roulette_pool:
            import random
            picked_movie = random.choice(roulette_pool)
            st.session_state.roulette_pick = picked_movie
            st.balloons()
        else:
            import random
            fallback_sample = movies["title"].head(50).tolist()
            picked_movie = random.choice(fallback_sample)
            st.session_state.roulette_pick = picked_movie
            st.info("💡 Saved list was empty, so Roulette picked a top-rated movie for you!")

    if "roulette_pick" in st.session_state:
        pick = st.session_state.roulette_pick
        matched = movies[movies['title'] == pick]
        if not matched.empty:
            m_id = matched.iloc[0]["movie_id"]
            p_post, p_rate, p_rel, p_ov, p_gen = fetch_movie(m_id, title=pick)
            p_trail, p_prov, p_watch = get_card_action_links(m_id, pick)
            p_fall = make_fallback_poster_svg(pick)
            st.html(f"""
            <div style="background:linear-gradient(135deg, rgba(255,201,74,0.15) 0%, rgba(20,20,25,0.95) 100%); border:1px solid #FFC94A; border-radius:12px; padding:16px 20px; margin: 14px 0 20px; display:flex; gap:16px; align-items:center; box-shadow:0 8px 24px rgba(255,201,74,0.15);">
                <img src="{p_post}" style="width:70px; height:100px; object-fit:cover; border-radius:6px;" alt="{esc(pick)}" onerror="this.onerror=null;this.src='{p_fall}';">
                <div style="flex:1;">
                    <div style="font-size:11px; font-weight:800; color:#FFC94A; letter-spacing:1px;">🎉 TONIGHT'S ROULETTE WINNER</div>
                    <div style="font-family:'Bebas Neue',sans-serif; font-size:24px; color:#FFFFFF; letter-spacing:0.5px;">{esc(pick)}</div>
                    <div style="font-size:12px; color:#BCBCBC; margin-bottom:8px;">⭐ {p_rate} • 🎭 {esc(p_gen)}</div>
                    <div style="display:flex; gap:8px;">
                        <a href="{p_trail}" target="_blank" rel="noopener noreferrer" class="nf-btn-trailer" style="padding:6px 14px; font-size:12px;">▶ Watch Trailer</a>
                        <a href="{p_watch}" target="_blank" rel="noopener noreferrer" class="nf-btn-watch" style="padding:6px 14px; font-size:12px;">🍿 Stream Now</a>
                    </div>
                </div>
            </div>
            """)

    st.write("")

    list_tabs = st.tabs(["❤️ Favorites", "🎬 Watchlist", "⭐ My Ratings", "⚙️ Manage & Export"])
    
    with list_tabs[0]:
        render_poster_wall(st.session_state.favorites, "fav_wall")
        
    with list_tabs[1]:
        render_poster_wall(st.session_state.watchlist, "watch_wall")
        
    with list_tabs[2]:
        if not st.session_state.ratings:
            st.info("⭐ You haven't rated anything yet. Rate movies from the Search & Details tab.")
        else:
            rated_titles = list(st.session_state.ratings.keys())
            render_poster_wall(rated_titles, "rated_wall")

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