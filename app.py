import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Music Stats + Recommender", layout="wide")

# ---------------------------
# PITCH BLACK THEME
# ---------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #000000;
            color: #f5f5f5;
        }
        h1, h2, h3, h4, p, label, span, div {
            color: #f5f5f5 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #000000;
        }
        .metric-card {
            background: #0a0a0a;
            border: 1px solid #222222;
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎧 Music Dataset Dashboard")
st.caption("Statistics + recommendation engine in one black-theme app.")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("rym_clean1.csv")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
    st.stop()

# ---------------------------
# COLUMN SETUP
# ---------------------------
album_col = "release_name"
artist_col = "artist_name"
genre_col_1 = "primary_genres"
genre_col_2 = "secondary_genres"
rating_col = "avg_rating"
count_col = "rating_count"
review_col = "review_count"
release_type_col = "release_type"

required_cols = [album_col, artist_col, rating_col, count_col]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# Optional columns handling
for col in [album_col, artist_col, genre_col_1, genre_col_2, release_type_col]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown").astype(str)

for col in [rating_col, count_col, review_col]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[album_col, artist_col, rating_col, count_col]).copy()

# ---------------------------
# HELPERS
# ---------------------------
def parse_genres(series: pd.Series) -> pd.Series:
    s = series.fillna("").astype(str)
    s = s.str.split(",").explode().str.strip()
    s = s[(s != "") & (s.str.lower() != "nan")]
    return s.str.lower()

def apply_dark_fig(fig):
    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#f5f5f5"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(font=dict(color="#f5f5f5")),
    )
    return fig

def normalize(series: pd.Series) -> pd.Series:
    series = series.astype(float)
    mn = series.min()
    mx = series.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - mn) / (mx - mn)

def build_row_genres(row) -> set:
    g1 = str(row.get(genre_col_1, "")).lower()
    g2 = str(row.get(genre_col_2, "")).lower()
    combined = f"{g1}, {g2}"
    tokens = [g.strip() for g in combined.split(",")]
    return set([g for g in tokens if g and g != "unknown" and g != "nan"])

# ---------------------------
# PRECOMPUTE STATS
# ---------------------------
total_albums = len(df)
total_artists = df[artist_col].nunique()
avg_rating_all = df[rating_col].mean()
total_ratings = df[count_col].sum()
avg_reviews = df[review_col].mean() if review_col in df.columns else None

best_rated_album = df.sort_values(by=[rating_col, count_col], ascending=[False, False]).iloc[0]
most_rated_album = df.sort_values(by=count_col, ascending=False).iloc[0]

artist_rating_counts = df.groupby(artist_col)[count_col].sum().sort_values(ascending=False)
most_rated_artist_name = artist_rating_counts.index[0]
most_rated_artist_count = int(artist_rating_counts.iloc[0])

genres = pd.concat(
    [
        parse_genres(df[genre_col_1]) if genre_col_1 in df.columns else pd.Series(dtype=str),
        parse_genres(df[genre_col_2]) if genre_col_2 in df.columns else pd.Series(dtype=str),
    ],
    ignore_index=True,
)
genre_counts = genres.value_counts().head(10)

if len(genre_counts) > 0:
    top_genre = genre_counts.index[0]
    top_genre_count = int(genre_counts.iloc[0])
else:
    top_genre = "Unknown"
    top_genre_count = 0

palette = [
    "#27364a", "#2f4858", "#3b4a5a", "#4a3f58", "#3f514a",
    "#5a4a3a", "#334d4f", "#4b3947", "#2f3f52", "#4a4538"
]

# ---------------------------
# TABS
# ---------------------------
tab_stats, tab_reco = st.tabs(["📊 Statistics", "🎯 Recommendation"])

# =========================================================
# STATISTICS TAB
# =========================================================
with tab_stats:
    st.subheader("Key Stats")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Best Rated Album", best_rated_album[album_col], f"{best_rated_album[rating_col]:.2f}")
        st.caption(best_rated_album[artist_col])

    with c2:
        st.metric("Most Popular Genre", top_genre, f"{top_genre_count} mentions")

    with c3:
        st.metric("Most Rated Artist", most_rated_artist_name, f"{most_rated_artist_count:,} ratings")

    with c4:
        st.metric("Most Rated Album", most_rated_album[album_col], f"{int(most_rated_album[count_col]):,} ratings")
        st.caption(most_rated_album[artist_col])

    st.divider()

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("Total Albums", f"{total_albums:,}")
    with c6:
        st.metric("Total Artists", f"{total_artists:,}")
    with c7:
        st.metric("Average Rating", f"{avg_rating_all:.2f}")
    with c8:
        st.metric("Total Ratings", f"{int(total_ratings):,}")

    if avg_reviews is not None and pd.notna(avg_reviews):
        st.caption(f"Average review count per album: {avg_reviews:.1f}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Top 10 Genres")
        genre_fig = px.bar(
            x=genre_counts.index,
            y=genre_counts.values,
            text=genre_counts.values,
            color=genre_counts.index,
            color_discrete_sequence=palette,
            labels={"x": "Genre", "y": "Count"},
        )
        genre_fig = apply_dark_fig(genre_fig)
        genre_fig.update_traces(textposition="outside", marker_line_color="#000000", marker_line_width=1)
        genre_fig.update_layout(showlegend=False, xaxis_tickangle=-35, height=420)
        st.plotly_chart(genre_fig, use_container_width=True)

    with right:
        st.subheader("Rating Distribution")
        hist_fig = px.histogram(
            df,
            x=rating_col,
            nbins=30,
            color_discrete_sequence=["#40576d"],
            labels={rating_col: "Average Rating"},
        )
        hist_fig = apply_dark_fig(hist_fig)
        hist_fig.update_traces(marker_line_color="#000000", marker_line_width=1)
        hist_fig.update_layout(height=420)
        st.plotly_chart(hist_fig, use_container_width=True)

    left2, right2 = st.columns(2)

    with left2:
        st.subheader("Top 10 Artists by Rating Count")
        top_artists = artist_rating_counts.head(10)
        artist_fig = px.bar(
            x=top_artists.index,
            y=top_artists.values,
            text=top_artists.values,
            color=top_artists.index,
            color_discrete_sequence=palette,
            labels={"x": "Artist", "y": "Rating Count"},
        )
        artist_fig = apply_dark_fig(artist_fig)
        artist_fig.update_traces(textposition="outside", marker_line_color="#000000", marker_line_width=1)
        artist_fig.update_layout(showlegend=False, xaxis_tickangle=-35, height=420)
        st.plotly_chart(artist_fig, use_container_width=True)

    with right2:
        st.subheader("Release Type Breakdown")
        if release_type_col in df.columns:
            release_counts = df[release_type_col].value_counts().head(8)
            donut_fig = go.Figure(
                data=[
                    go.Pie(
                        labels=release_counts.index,
                        values=release_counts.values,
                        hole=0.5,
                        textinfo="label+percent",
                        textfont=dict(color="#f5f5f5"),
                        marker=dict(colors=palette[: len(release_counts)]),
                    )
                ]
            )
            donut_fig = apply_dark_fig(donut_fig)
            donut_fig.update_layout(height=420)
            st.plotly_chart(donut_fig, use_container_width=True)
        else:
            st.info("No release_type column found.")

    st.subheader("Rating Count vs Average Rating")
    scatter_df = df[[album_col, artist_col, rating_col, count_col]].dropna().copy()
    scatter_fig = px.scatter(
        scatter_df,
        x=count_col,
        y=rating_col,
        hover_data=[album_col, artist_col],
        color_discrete_sequence=["#596f85"],
        labels={count_col: "Rating Count", rating_col: "Average Rating"},
    )
    scatter_fig = apply_dark_fig(scatter_fig)
    scatter_fig.update_traces(marker=dict(size=8, opacity=0.7, line=dict(width=0.5, color="#000000")))
    scatter_fig.update_layout(height=500)
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.subheader("Top 10 Albums by Average Rating")
    top_rated_albums = df.sort_values(by=[rating_col, count_col], ascending=[False, False]).head(10)
    top_album_fig = px.bar(
        top_rated_albums,
        x=album_col,
        y=rating_col,
        text=rating_col,
        color=album_col,
        color_discrete_sequence=palette,
        labels={album_col: "Album", rating_col: "Average Rating"},
    )
    top_album_fig = apply_dark_fig(top_album_fig)
    top_album_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_line_color="#000000", marker_line_width=1)
    top_album_fig.update_layout(showlegend=False, xaxis_tickangle=-35, height=500)
    st.plotly_chart(top_album_fig, use_container_width=True)

    with st.expander("Dataset Preview"):
        st.dataframe(df.head(20), use_container_width=True)

# =========================================================
# RECOMMENDATION TAB
# =========================================================
with tab_reco:
    st.subheader("Build a recommendation profile")

    all_genres = sorted(
        pd.unique(
            pd.concat(
                [
                    parse_genres(df[genre_col_1]) if genre_col_1 in df.columns else pd.Series(dtype=str),
                    parse_genres(df[genre_col_2]) if genre_col_2 in df.columns else pd.Series(dtype=str),
                ],
                ignore_index=True,
            )
        )
    )

    album_options = df[album_col].dropna().astype(str).sort_values().unique().tolist()

    with st.form("recommendation_form"):
        c1, c2 = st.columns(2)

        with c1:
            user_type = st.selectbox("Listener Type", ["Casual", "Enjoyer", "Snob"])
            preferred_genre = st.selectbox("Preferred Genre", ["Any genre"] + all_genres)
            liked_albums = st.multiselect(
                "Albums You Like",
                options=album_options,
                help="Pick 1 to 5 albums. More signals give better recommendations.",
            )

        with c2:
            min_rating = st.slider("Minimum Average Rating", 0.0, 5.0, 3.5, 0.1)
            min_popularity = st.slider(
                "Minimum Rating Count",
                0,
                int(df[count_col].max()),
                int(df[count_col].median()),
            )
            n_recs = st.slider("Number of Recommendations", 5, 15, 10)

        submitted = st.form_submit_button("Generate Recommendations")

    def recommend(
        df_in: pd.DataFrame,
        liked_albums_in,
        preferred_genre_in: str,
        user_type_in: str,
        min_rating_in: float,
        min_popularity_in: int,
        n_recs_in: int,
    ) -> pd.DataFrame:
        work = df_in.copy()

        # Basic filters
        work = work[work[rating_col] >= min_rating_in]
        work = work[work[count_col] >= min_popularity_in]
        work = work[~work[album_col].isin(liked_albums_in)]

        # Genre preference filter
        if preferred_genre_in != "Any genre":
            if genre_col_1 in work.columns and genre_col_2 in work.columns:
                mask = (
                    work[genre_col_1].str.lower().str.contains(preferred_genre_in.lower(), na=False)
                    | work[genre_col_2].str.lower().str.contains(preferred_genre_in.lower(), na=False)
                )
                work = work[mask]

        if work.empty:
            return work

        # Build liked genre set
        liked_genres = set()
        if liked_albums_in:
            liked_rows = df_in[df_in[album_col].isin(liked_albums_in)]
            for _, row in liked_rows.iterrows():
                liked_genres |= build_row_genres(row)

        # Precompute normalized values
        work = work.copy()
        work["rating_norm"] = normalize(work[rating_col])
        work["count_norm"] = normalize(work[count_col])

        # Weights by listener type
        weights = {
            "Casual": {"popularity": 0.55, "rating": 0.25, "genre": 0.20},
            "Enjoyer": {"popularity": 0.35, "rating": 0.35, "genre": 0.30},
            "Snob": {"popularity": 0.15, "rating": 0.65, "genre": 0.20},
        }[user_type_in]

        # Score each row
        scores = []
        reasons = []

        for _, row in work.iterrows():
            row_genres = build_row_genres(row)

            preferred_bonus = 1.0 if (preferred_genre_in != "Any genre" and preferred_genre_in.lower() in row_genres) else 0.0
            liked_overlap = len(row_genres & liked_genres)
            liked_bonus = min(liked_overlap / 3.0, 1.0) if liked_genres else 0.0

            score = (
                weights["popularity"] * float(row["count_norm"])
                + weights["rating"] * float(row["rating_norm"])
                + weights["genre"] * (0.6 * preferred_bonus + 0.4 * liked_bonus)
            )

            score += 0.03 * liked_overlap

            scores.append(score)

            reason_parts = []
            if preferred_bonus > 0:
                reason_parts.append(f"matches {preferred_genre_in}")
            if liked_overlap > 0:
                reason_parts.append(f"shares {liked_overlap} genre(s) with liked albums")
            if row[rating_col] >= 4.0:
                reason_parts.append("strong rating")
            if row[count_col] >= min_popularity_in:
                reason_parts.append("popular enough")
            reasons.append(", ".join(reason_parts) if reason_parts else "balanced fit")

        work["score"] = scores
        work["reason"] = reasons

        return work.sort_values(by=["score", rating_col, count_col], ascending=[False, False, False]).head(n_recs_in)

    if submitted:
        if len(liked_albums) == 0:
            st.warning("Pick at least 1 album you like.")
        else:
            if len(liked_albums) > 5:
                st.warning("Keep it to 5 albums max. I am using the first 5 you selected.")
                liked_albums = liked_albums[:5]

            results = recommend(
                df,
                liked_albums,
                preferred_genre,
                user_type,
                min_rating,
                min_popularity,
                n_recs,
            )

            if results.empty:
                st.warning("No results found. Try lowering your filters.")
            else:
                st.success(f"Found {len(results)} recommendations.")

                # Recommendation table
                display_cols = [album_col, artist_col, rating_col, count_col, "score", "reason"]
                show_df = results[display_cols].copy()
                show_df[rating_col] = show_df[rating_col].round(2)
                show_df["score"] = show_df["score"].round(3)
                st.dataframe(show_df, use_container_width=True)

                # Recommendation ranking chart
                rec_chart = px.bar(
                    results.sort_values("score", ascending=True),
                    x="score",
                    y=album_col,
                    orientation="h",
                    color="score",
                    color_continuous_scale=["#1e2a35", "#41586d", "#6b7f91"],
                    labels={"score": "Recommendation Score", album_col: "Album"},
                )
                rec_chart = apply_dark_fig(rec_chart)
                rec_chart.update_layout(height=500, coloraxis_showscale=False)
                st.plotly_chart(rec_chart, use_container_width=True)

                st.subheader("Recommendation Cards")
                for _, row in results.iterrows():
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="margin-bottom: 6px;">{row[album_col]}</h4>
                            <p style="margin-bottom: 4px;">Artist: {row[artist_col]}</p>
                            <p style="margin-bottom: 4px;">Average Rating: {row[rating_col]:.2f}</p>
                            <p style="margin-bottom: 4px;">Rating Count: {int(row[count_col]):,}</p>
                            <p style="margin-bottom: 0;">Why: {row["reason"]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.write("")

    st.subheader("How the scoring works")
    st.write(
        "Casual leans toward popularity, Enjoyer is balanced, and Snob leans toward rating quality. "
        "Your liked albums and preferred genre push the results toward your taste shape."
    )
