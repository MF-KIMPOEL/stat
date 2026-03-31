import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Music Stats Dashboard", layout="wide")

# ---------------------------
# Dark theme styling
# ---------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #000000;
            color: #e6e6e6;
        }
        h1, h2, h3, h4, p, label, span, div {
            color: #e6e6e6 !important;
        }
        .metric-box {
            background: #111822;
            border: 1px solid #223042;
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        }
        section[data-testid="stSidebar"] {
            background-color: #0b0f14;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Page title
# ---------------------------
st.title("🎧 Music Dataset Statistics")
st.caption("Dark-theme dashboard for your CSV with clean stats and multiple chart styles.")

# ---------------------------
# Load data
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
# Fixed column names from your dataset
# ---------------------------
album_col = "release_name"
artist_col = "artist_name"
genre_col_1 = "primary_genres"
genre_col_2 = "secondary_genres"
rating_col = "avg_rating"
count_col = "rating_count"
review_col = "review_count"
release_type_col = "release_type"
date_col = "release_date"

# ---------------------------
# Basic cleaning
# ---------------------------
for col in [album_col, artist_col, genre_col_1, genre_col_2, release_type_col]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown").astype(str)

for col in [rating_col, count_col, review_col]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[album_col, artist_col, rating_col, count_col])

# ---------------------------
# Helpers
# ---------------------------
def parse_genres(series: pd.Series) -> pd.Series:
    s = series.fillna("").astype(str)
    s = s.str.split(",").explode().str.strip()
    s = s[(s != "") & (s.str.lower() != "nan")]
    return s

def apply_dark_fig(fig):
    fig.update_layout(
        paper_bgcolor="#0b0f14",
        plot_bgcolor="#0b0f14",
        font=dict(color="#e6e6e6"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(font=dict(color="#e6e6e6"))
    )
    return fig

# muted, darker palette
palette = [
    "#27364a", "#2f4858", "#3b4a5a", "#4a3f58", "#3f514a",
    "#5a4a3a", "#334d4f", "#4b3947", "#2f3f52", "#4a4538"
]

# ---------------------------
# Extra stats
# ---------------------------
total_albums = len(df)
total_artists = df[artist_col].nunique()
avg_rating_all = df[rating_col].mean()
total_ratings = df[count_col].sum()
avg_reviews = df[review_col].mean() if review_col in df.columns else None

best_rated_row = df.sort_values(by=[rating_col, count_col], ascending=[False, False]).iloc[0]
most_rated_album_row = df.sort_values(by=count_col, ascending=False).iloc[0]

top_artist_series = df.groupby(artist_col)[count_col].sum().sort_values(ascending=False)
most_rated_artist_name = top_artist_series.index[0]
most_rated_artist_count = int(top_artist_series.iloc[0])

genres = pd.concat(
    [parse_genres(df[genre_col_1]), parse_genres(df[genre_col_2])],
    ignore_index=True
)
genre_counts = genres.value_counts().head(10)

top_genre = genre_counts.index[0]
top_genre_count = int(genre_counts.iloc[0])

# ---------------------------
# KPI cards
# ---------------------------
st.subheader("Key Stats")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Best Rated Album", best_rated_row[album_col], f"{best_rated_row[rating_col]:.2f}")
    st.caption(best_rated_row[artist_col])

with c2:
    st.metric("Most Popular Genre", top_genre, f"{top_genre_count} mentions")

with c3:
    st.metric("Most Rated Artist", most_rated_artist_name, f"{most_rated_artist_count:,} ratings")

with c4:
    st.metric("Most Rated Album", most_rated_album_row[album_col], f"{int(most_rated_album_row[count_col]):,} ratings")
    st.caption(most_rated_album_row[artist_col])

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

# ---------------------------
# Charts row 1
# ---------------------------
left, right = st.columns(2)

with left:
    st.subheader("Top 10 Genres")
    genre_fig = px.bar(
        x=genre_counts.index,
        y=genre_counts.values,
        labels={"x": "Genre", "y": "Count"},
        text=genre_counts.values,
        color=genre_counts.index,
        color_discrete_sequence=palette
    )
    genre_fig = apply_dark_fig(genre_fig)
    genre_fig.update_traces(textposition="outside", marker_line_color="#0b0f14", marker_line_width=1)
    genre_fig.update_layout(showlegend=False, xaxis_tickangle=-35, height=420)
    st.plotly_chart(genre_fig, use_container_width=True)

with right:
    st.subheader("Rating Distribution")
    hist_fig = px.histogram(
        df,
        x=rating_col,
        nbins=30,
        labels={rating_col: "Average Rating"},
        opacity=0.9,
        color_discrete_sequence=["#4a5f75"]
    )
    hist_fig = apply_dark_fig(hist_fig)
    hist_fig.update_traces(marker_line_color="#0b0f14", marker_line_width=1)
    hist_fig.update_layout(height=420)
    st.plotly_chart(hist_fig, use_container_width=True)

# ---------------------------
# Charts row 2
# ---------------------------
left2, right2 = st.columns(2)

with left2:
    st.subheader("Top 10 Artists by Rating Count")
    top_artists = top_artist_series.head(10)
    artist_fig = px.bar(
        x=top_artists.index,
        y=top_artists.values,
        labels={"x": "Artist", "y": "Rating Count"},
        text=top_artists.values,
        color=top_artists.index,
        color_discrete_sequence=palette
    )
    artist_fig = apply_dark_fig(artist_fig)
    artist_fig.update_traces(textposition="outside", marker_line_color="#0b0f14", marker_line_width=1)
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
                    textfont=dict(color="#e6e6e6"),
                    marker=dict(colors=palette[:len(release_counts)])
                )
            ]
        )
        donut_fig = apply_dark_fig(donut_fig)
        donut_fig.update_layout(height=420)
        st.plotly_chart(donut_fig, use_container_width=True)
    else:
        st.info("No release_type column found.")

# ---------------------------
# Charts row 3
# ---------------------------
st.subheader("Rating Count vs Average Rating")
scatter_df = df[[album_col, artist_col, rating_col, count_col]].dropna().copy()
scatter_df["log_rating_count"] = scatter_df[count_col].clip(lower=1)

scatter_fig = px.scatter(
    scatter_df,
    x=count_col,
    y=rating_col,
    hover_data=[album_col, artist_col],
    labels={count_col: "Rating Count", rating_col: "Average Rating"},
    color_discrete_sequence=["#566c84"]
)
scatter_fig = apply_dark_fig(scatter_fig)
scatter_fig.update_traces(marker=dict(size=8, opacity=0.7, line=dict(width=0.5, color="#0b0f14")))
scatter_fig.update_layout(height=500)
st.plotly_chart(scatter_fig, use_container_width=True)

# ---------------------------
# Albums with highest ratings
# ---------------------------
st.subheader("Top 10 Albums by Average Rating")
top_rated_albums = df.sort_values(by=[rating_col, count_col], ascending=[False, False]).head(10)

top_album_fig = px.bar(
    top_rated_albums,
    x=album_col,
    y=rating_col,
    text=rating_col,
    labels={album_col: "Album", rating_col: "Average Rating"},
    color=album_col,
    color_discrete_sequence=palette
)
top_album_fig = apply_dark_fig(top_album_fig)
top_album_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_line_color="#0b0f14", marker_line_width=1)
top_album_fig.update_layout(showlegend=False, xaxis_tickangle=-35, height=500)
st.plotly_chart(top_album_fig, use_container_width=True)

# ---------------------------
# Data preview
# ---------------------------
with st.expander("Dataset Preview"):
    st.dataframe(df.head(20), use_container_width=True)
