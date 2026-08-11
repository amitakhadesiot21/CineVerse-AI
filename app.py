import streamlit as st
import pandas as pd
import requests
import pickle
import json
import os
import random
from datetime import datetime

# -------------------------------------------------
# PAGE CONFIG (must be first Streamlit call)
# -------------------------------------------------

st.set_page_config(
    page_title="🎬 CineVerse AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("styles.css not found — running with default Streamlit styling.")


load_css()

# -------------------------------------------------
# TMDB API KEY
# -------------------------------------------------

API_KEY = st.secrets["TMDB_API_KEY"]

TMDB_BASE = "https://api.themoviedb.org/3"
DATA_FILE = "user_data.json"

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


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_movie(movie_id):
    """Fetch poster/rating/overview/genres for a movie. Cached for 24h so
    the same movie never triggers a duplicate API call in a session."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            raise Exception("API Error")

        data = response.json()

        poster = (
            "https://image.tmdb.org/t/p/w500" + data["poster_path"]
            if data.get("poster_path")
            else "https://via.placeholder.com/300x450?text=No+Poster"
        )

        rating = data.get("vote_average", "N/A")
        release = data.get("release_date", "Unknown")
        overview = data.get("overview", "No description available.")
        genres = ", ".join(g["name"] for g in data.get("genres", [])) or "Unknown"

        return poster, rating, release, overview, genres

    except Exception:
        return (
            "https://via.placeholder.com/300x450?text=No+Poster",
            "N/A",
            "Unknown",
            "Unable to fetch movie details.",
            "Unknown",
        )


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
    btn_label = f"✔ In {label}" if is_in else f"{icon} {label}"
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
    moviePoster, movieRating, movieRelease, _, movieGenres = fetch_movie(
        movie["movie_id"]
    )

    year = movieRelease[:4] if movieRelease != "Unknown" else "N/A"

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
    except:
        rating_display = movieRating

    rating_class = rating_bucket(movieRating)

    # Genre
    genre = (
        movieGenres.split(",")[0].strip()
        if movieGenres and movieGenres != "Unknown"
        else "Unknown"
    )

    # Escape text that comes from movie data
    title = str(movie["title"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    card_html = f"""
    <div class="poster-card">

        <img
            src="{moviePoster}"
            class="poster-image"
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

        </div>

    </div>
    """

    with col:

        # IMPORTANT:
        # Use st.html instead of st.markdown
        st.html(card_html)

        list_button(
            movie["title"],
            "favorites",
            "Fav",
            "❤️",
            key=f"{key_prefix}_fav_{index}_{movie['movie_id']}"
        )


@st.cache_data(ttl=86400, show_spinner=False)
def get_genre_map():
    """name -> id, for the genre filter UI."""
    try:
        r = requests.get(f"{TMDB_BASE}/genre/movie/list", params={"api_key": API_KEY}, timeout=10)
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
        if mode == "trending":
            url, params = f"{TMDB_BASE}/trending/movie/week", {"api_key": API_KEY}
        elif mode == "top_rated":
            url, params = f"{TMDB_BASE}/movie/top_rated", {"api_key": API_KEY}
        else:
            url = f"{TMDB_BASE}/discover/movie"
            params = {"api_key": API_KEY, "with_genres": genre_id, "sort_by": "popularity.desc"}

        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return []
        return r.json().get("results", [])[:10]
    except Exception:
        return []


@st.cache_data(ttl=86400, show_spinner=False)
def get_credits(movie_id):
    """Top billed cast for a movie, with headshots."""
    try:
        r = requests.get(f"{TMDB_BASE}/movie/{movie_id}/credits", params={"api_key": API_KEY}, timeout=10)
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
                    else "https://via.placeholder.com/200x200?text=%3F"
                ),
            }
            for c in cast
        ]
    except Exception:
        return []


@st.cache_data(ttl=86400, show_spinner=False)
def get_trailer_url(movie_id):
    """Official YouTube trailer URL, or None if not found."""
    try:
        r = requests.get(f"{TMDB_BASE}/movie/{movie_id}/videos", params={"api_key": API_KEY}, timeout=10)
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
def find_tmdb_movie(title):
    """Find a TMDB movie ID using its title."""
    try:
        r = requests.get(
            f"{TMDB_BASE}/search/movie",
            params={
                "api_key": API_KEY,
                "query": title,
                "include_adult": False,
            },
            timeout=10,
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
        r = requests.get(
            f"{TMDB_BASE}/movie/{movie_id}/recommendations",
            params={
                "api_key": API_KEY,
            },
            timeout=10,
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
    poster = (
        "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
        if movie.get("poster_path")
        else "https://via.placeholder.com/300x450?text=No+Poster"
    )

    rating = movie.get("vote_average", "N/A")

    if isinstance(rating, (int, float)):
        rating_display = round(rating, 1)
    else:
        rating_display = rating

    year = (movie.get("release_date") or "")[:4] or "N/A"

    title = movie.get("title") or movie.get("name") or "Unknown"

    ribbon_html = (
        '<span class="new-ribbon">NEW</span>'
        if is_new_release(year)
        else ""
    )

    rating_class = rating_bucket(rating)

    safe_title = (
        str(title)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    card_html = f"""
    <div class="poster-card">

        <img
            src="{poster}"
            class="poster-image"
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
            key=f"{key_prefix}_fav_{index}_{movie.get('id')}"
        )

# -------------------------------------------------
# HERO
# -------------------------------------------------

st.caption("✨ Discover • Explore • Watch • Enjoy")

st.markdown(
    """
    <div class="hero">
        <div class="hero-glow hero-glow-a"></div>
        <div class="hero-glow hero-glow-b"></div>
        <h1>🎬 CineVerse AI</h1>
        <p>Discover Movies Powered By Artificial Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

with st.sidebar:
    st.title("🎬 CineVerse")
    st.success("AI Recommendation Engine")

    st.metric("Movies", len(movies))
    st.metric("Favorites", len(st.session_state.favorites))
    st.metric("Watchlist", len(st.session_state.watchlist))
    st.metric("Rated", len(st.session_state.ratings))

    st.divider()

    if st.button("🎲 Surprise Movie", use_container_width=True):
        st.session_state.random_movie = movies.sample(1).iloc[0]
        st.rerun()

    st.info(f"🎲 Try: **{st.session_state.random_movie['title']}**")

    st.divider()
    st.write("### ❤️ Favorites")
    if not st.session_state.favorites:
        st.caption("No favorites yet.")
    else:
        for movie in st.session_state.favorites:
            st.write("•", movie)

    st.divider()
    st.write("### About")
    st.caption("Developed by")
    st.caption("Amit Akhade")
    st.caption("CineVerse AI v2.1")

# -------------------------------------------------
# TABS
# -------------------------------------------------

tab_pick, tab_search, tab_reco, tab_discover, tab_compare, tab_lists, tab_dash = st.tabs(
    [
        "🌟 Today's Pick",
        "🔍 Search & Details",
        "🎯 Recommendations",
        "🔥 Discover",
        "⚖️ Compare",
        "📋 My Lists",
        "📊 Dashboard",
    ]
)

# ---------------- TODAY'S PICK ----------------
with tab_pick:
    if st.button("🎲 Surprise Me", use_container_width=True, key="surprise_main"):
        st.session_state.random_movie = movies.sample(1).iloc[0]
        st.rerun()

    random_movie = st.session_state.random_movie
    poster, rating, release, overview, genres = fetch_movie(random_movie["movie_id"])
    year = release[:4] if release != "Unknown" else "N/A"

    left, right = st.columns([1, 2])
    with left:
        st.markdown(
            f"""
            <div class="poster-hero" style="--poster-url:url('{poster}')">
                <span class="rating-badge {rating_bucket(rating)}">⭐ {rating}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(f"### 🎬 {random_movie['title']}")
        c1, c2 = st.columns(2)
        c1.metric("⭐ Rating", rating)
        c2.metric("📅 Year", year)
        st.caption(f"🎭 {genres}")
        short_overview = overview[:220] + "..." if len(overview) > 220 else overview
        st.write(short_overview)

        st.write("")
        list_button(random_movie["title"], "favorites", "Favorite", "❤️", key="fav_pick")
        render_trailer_block(random_movie["movie_id"], random_movie["title"])

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
    poster, rating, release, overview, genres = fetch_movie(selected["movie_id"])

    st.divider()
    left, right = st.columns([1, 2])

    with left:
        st.markdown(
            f"""
            <div class="poster-hero" style="--poster-url:url('{poster}')">
                <span class="rating-badge {rating_bucket(rating)}">⭐ {rating}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.title(selected["title"])

        c1, c2, c3 = st.columns(3)
        c1.metric("⭐ Rating", rating)
        c2.metric("📅 Release", release[:4] if release != "Unknown" else "N/A")
        c3.metric("🎭 Genres", len(genres.split(",")) if genres != "Unknown" else 0)

        st.markdown("### Overview")
        st.write(overview)

        if genres != "Unknown":
            st.markdown(
                " ".join(f'<span class="genre">{g.strip()}</span>' for g in genres.split(",")),
                unsafe_allow_html=True,
            )

        st.write("")
        colA, colB = st.columns(2)
        with colA:
            list_button(selected["title"], "favorites", "Favorite", "❤️", key="fav_detail")
        with colB:
            list_button(selected["title"], "watchlist", "Watchlist", "📋", key="watch_detail")

        st.write("")
        st.markdown("### ⭐ Your Rating")
        rate_movie(selected["title"], key="rate_detail")

    st.divider()
    st.markdown("### 🎭 Top Cast")
    render_cast_row(get_credits(selected["movie_id"]))

    st.divider()
    st.markdown("### ▶ Trailer")
    render_trailer_block(selected["movie_id"], selected["title"])

# ---------------- RECOMMENDATIONS ----------------
with tab_reco:
    st.subheader("🎯 Get AI Recommendations")
    st.caption(f"Based on your selection: **{st.session_state.get('last_selected', selected_movie)}**")

    num_reco = st.slider("How many recommendations?", min_value=5, max_value=20, value=10, step=5)
    recommend_btn = st.button("🎬 Generate AI Recommendations", use_container_width=True)

    if recommend_btn:
        base_movie = st.session_state.get("last_selected", selected_movie)
        with st.spinner("🤖 AI is finding similar movies..."):
            recommendations = recommend(base_movie, top_n=num_reco)

        st.session_state.history.append(
            {"movie": base_movie, "count": num_reco, "time": datetime.now().strftime("%d-%m-%Y %H:%M")}
        )
        st.session_state.last_recommendations = recommendations
        st.success(f"Top {len(recommendations)} Movies Found!")

    if "last_recommendations" in st.session_state:
        recommendations = st.session_state.last_recommendations
        st.markdown("<h2 style='text-align:center'>🍿 AI Recommended Movies</h2>", unsafe_allow_html=True)

        per_row = 5
        for row_start in range(0, len(recommendations), per_row):
            row_movies = recommendations.iloc[row_start: row_start + per_row]
            cols = st.columns(per_row)
            for i, (_, movie) in enumerate(row_movies.iterrows()):
                render_grid_card(movie, cols[i], row_start + i, key_prefix="reco")

# ---------------- DISCOVER ----------------
with tab_discover:

    st.subheader("🔥 Discover")

    # =================================================
    # BECAUSE YOU LIKED
    # =================================================

    if st.session_state.favorites:

        st.markdown(
            """
            <div class="discover-heading">
                <h2>💡 Because You Liked...</h2>
                <p>Personalized recommendations based on your favorite movies</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Select and remember random favorites
        if "discover_favorite_picks" not in st.session_state:

            pick_count = min(
                2,
                len(st.session_state.favorites)
            )

            st.session_state.discover_favorite_picks = (
                pd.Series(
                    st.session_state.favorites
                )
                .sample(n=pick_count)
                .tolist()
            )

        # Shuffle button
        if st.button(
            "🔄 Shuffle Picks",
            use_container_width=True,
            key="shuffle_discover"
        ):

            pick_count = min(
                2,
                len(st.session_state.favorites)
            )

            st.session_state.discover_favorite_picks = (
                pd.Series(
                    st.session_state.favorites
                )
                .sample(n=pick_count)
                .tolist()
            )

            st.rerun()

        # Show recommendations for selected favorites
        for fav_title in st.session_state.discover_favorite_picks:

            if fav_title in movies["title"].values:

                st.markdown(
                    f"""
                    <div class="because-liked">
                        ❤️ Because you liked:
                        <b>{fav_title}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                recs = recommend(
                    fav_title,
                    top_n=5
                )

                cols = st.columns(5)

                for i, (_, movie) in enumerate(
                    recs.iterrows()
                ):

                    render_grid_card(
                        movie,
                        cols[i],
                        i,
                        key_prefix=f"because_{fav_title}"
                    )

    else:

        st.info(
            "❤️ Add movies to your Favorites to get personalized recommendations."
        )

    # =================================================
    # SEPARATION
    # =================================================

    st.markdown(
        """
        <div class="discover-divider"></div>

        <div class="discover-main-heading">
            <h2>🔥 Discover More Movies</h2>
            <p>Explore trending, top-rated and genre-based movies</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =================================================
    # NORMAL DISCOVER
    # =================================================

    mode_label = st.radio(
        "Browse",
        [
            "Trending This Week",
            "Top Rated",
            "By Genre"
        ],
        horizontal=True,
        key="discover_mode",
    )

    genre_id = None

    if mode_label == "By Genre":

        genre_map = get_genre_map()

        if genre_map:

            genre_name = st.selectbox(
                "Pick a genre",
                list(genre_map.keys()),
                key="discover_genre"
            )

            genre_id = genre_map[genre_name]

        else:

            st.warning(
                "Couldn't load the genre list right now."
            )

    mode_key = {
        "Trending This Week": "trending",
        "Top Rated": "top_rated",
        "By Genre": "genre"
    }[mode_label]

    if mode_key != "genre" or genre_id:

        with st.spinner("Fetching movies..."):

            results = discover_movies(
                mode=mode_key,
                genre_id=genre_id
            )

        if not results:

            st.info(
                "No results right now."
            )

        else:

            for row_start in range(
                0,
                len(results),
                5
            ):

                row = results[
                    row_start:row_start + 5
                ]

                cols = st.columns(5)

                for i, movie in enumerate(row):

                    render_discover_card(
                        movie,
                        cols[i],
                        row_start + i,
                        key_prefix=mode_key
                    )

# ---------------- COMPARE ----------------
with tab_compare:
    st.subheader("⚖️ Compare Movies")

    c1, c2 = st.columns(2)
    with c1:
        movie_a = st.selectbox("First movie", movies["title"].values, key="compare_a")
    with c2:
        default_b = 1 if len(movies) > 1 else 0
        movie_b = st.selectbox("Second movie", movies["title"].values, index=default_b, key="compare_b")

    if movie_a == movie_b:
        st.info("Pick two different movies to compare.")
    else:
        row_a = movies[movies["title"] == movie_a].iloc[0]
        row_b = movies[movies["title"] == movie_b].iloc[0]
        poster_a, rating_a, release_a, overview_a, genres_a = fetch_movie(row_a["movie_id"])
        poster_b, rating_b, release_b, overview_b, genres_b = fetch_movie(row_b["movie_id"])

        st.divider()
        colA, colB = st.columns(2)
        for col, title, poster, rating, release, genres in [
            (colA, movie_a, poster_a, rating_a, release_a, genres_a),
            (colB, movie_b, poster_b, rating_b, release_b, genres_b),
        ]:
            with col:
                st.markdown(
                    f"""
                    <div class="poster-hero" style="--poster-url:url('{poster}')">
                        <span class="rating-badge {rating_bucket(rating)}">⭐ {rating}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"#### {title}")
                year = release[:4] if release != "Unknown" else "N/A"
                st.caption(f"📅 {year} &nbsp;•&nbsp; 🎭 {genres}", unsafe_allow_html=True)

        st.divider()
        both_numeric = isinstance(rating_a, (int, float)) and isinstance(rating_b, (int, float))
        m1, m2 = st.columns(2)
        m1.metric(
            f"⭐ {movie_a}", rating_a,
            delta=round(rating_a - rating_b, 1) if both_numeric else None,
        )
        m2.metric(
            f"⭐ {movie_b}", rating_b,
            delta=round(rating_b - rating_a, 1) if both_numeric else None,
        )

        if both_numeric and rating_a != rating_b:
            winner = movie_a if rating_a > rating_b else movie_b
            st.success(f"🏆 **{winner}** has the higher rating!")
        elif both_numeric:
            st.info("It's a tie on rating!")

        with st.expander("📖 Compare overviews"):
            oc1, oc2 = st.columns(2)
            oc1.write(overview_a)
            oc2.write(overview_b)

# ---------------- MY LISTS ----------------
with tab_lists:
    st.subheader("❤️ Favorite Movies")
    if not st.session_state.favorites:
        st.info("❤️ Your favorites list is empty.\n\nStart exploring movies and save your favorites!")
    else:
        fav_cols = st.columns(4)
        for i, movie in enumerate(st.session_state.favorites):
            with fav_cols[i % 4]:
                st.success(movie)

    st.divider()
    st.subheader("📋 Watchlist")
    if not st.session_state.watchlist:
        st.info("📋 Your watchlist is empty.\n\nAdd movies to watch later.")
    else:
        watch_cols = st.columns(4)
        for i, movie in enumerate(st.session_state.watchlist):
            with watch_cols[i % 4]:
                st.warning(movie)

    st.divider()
    st.subheader("⭐ Your Ratings")
    if not st.session_state.ratings:
        st.info("⭐ You haven't rated anything yet. Rate movies from the Search & Details tab.")
    else:
        rate_cols = st.columns(4)
        for i, (title, score) in enumerate(st.session_state.ratings.items()):
            with rate_cols[i % 4]:
                st.markdown(f"**{title}**")
                st.markdown("⭐" * score + "☆" * (5 - score))

    st.divider()
    st.subheader("📤 Export")
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
                _, _, _, _, genres_str = fetch_movie(match.iloc[0]["movie_id"])
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