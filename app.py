import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Music Stats Dashboard", layout="wide")

# ---- DARK STYLE ----
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    h1, h2, h3, h4, p, label, span, div {
        color: #ffffff !important;
    }
    .metric-card {
        background: #161b22;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #2b313c;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎧 Music Dataset Statistics")

# ---- COLOR PALETTE ----
colors = [
    "#4ea1ff", "#7cdb7c", "#ffb347", "#ff6b6b",
    "#c77dff", "#ffd166", "#06d6a0", "#f72585",
    "#90dbf4", "#f4a261"
]

# ---- LOAD DATA ----
df = pd.read_csv("rym_clean1.csv")
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

# ---- COLUMN NAMES ----
album_col = "release_name"
artist_col = "artist_name"
genre_col_1 = "primary_genres"
genre_col_2 = "secondary_genres"
rating_col = "avg_rating"
count_col = "rating_count"

# ---- CLEAN DATA ----
df[genre_col_1] = df[genre_col_1].fillna("")
df[genre_col_2] = df[genre_col_2].fillna("")
df[artist_col] = df[artist_col].fillna("Unknown")
df[album_col] = df[album_col].fillna("Unknown")

# ---- COMPUTE STATS ----
best_rated_album = df.sort_values(by=[rating_col, count_col], ascending=[False, False]).iloc[0]
most_rated_album = df.sort_values(by=count_col, ascending=False).iloc[0]

top_artist_series = df.groupby(artist_col)[count_col].sum().sort_values(ascending=False)
top_artist_name = top_artist_series.index[0]
top_artist_count = int(top_artist_series.iloc[0])

# GENRE PROCESSING
genres = pd.concat([
    df[genre_col_1].astype(str),
    df[genre_col_2].astype(str)
], ignore_index=True)

genre_list = genres.str.split(",").explode().str.strip()
genre_list = genre_list[genre_list != ""]
genre_counts = genre_list.value_counts().head(10)

top_genre = genre_counts.index[0]
top_genre_count = int(genre_counts.iloc[0])

# ---- KPI CARDS ----
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("🏆 Best Rated Album",
              best_rated_album[album_col],
              f"{best_rated_album[rating_col]:.2f}")
    st.caption(best_rated_album[artist_col])

with c2:
    st.metric("🔥 Most Popular Genre",
              top_genre,
              f"{top_genre_count} mentions")

with c3:
    st.metric("🎤 Most Rated Artist",
              top_artist_name,
              f"{top_artist_count:,} ratings")

with c4:
    st.metric("💿 Most Rated Album",
              most_rated_album[album_col],
              f"{int(most_rated_album[count_col]):,} ratings")
    st.caption(most_rated_album[artist_col])

st.divider()

# ---- CHARTS ----
left, right = st.columns(2)

# GENRE CHART
with left:
    st.subheader("Top 10 Genres")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    fig1.patch.set_facecolor("#0e1117")
    ax1.set_facecolor("#0e1117")

    genre_colors = [colors[i % len(colors)] for i in range(len(genre_counts))]
    genre_counts.plot(kind="bar", ax=ax1, color=genre_colors)

    ax1.set_title("Most Popular Genres", color="white")
    ax1.tick_params(axis='x', rotation=45, colors='white')
    ax1.tick_params(axis='y', colors='white')
    for spine in ax1.spines.values():
        spine.set_color("white")

    st.pyplot(fig1)

# ARTIST CHART
with right:
    st.subheader("Top 10 Artists")
    top_artists = top_artist_series.head(10)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    fig2.patch.set_facecolor("#0e1117")
    ax2.set_facecolor("#0e1117")

    artist_colors = [colors[i % len(colors)] for i in range(len(top_artists))]
    top_artists.plot(kind="bar", ax=ax2, color=artist_colors)

    ax2.set_title("Most Rated Artists", color="white")
    ax2.tick_params(axis='x', rotation=45, colors='white')
    ax2.tick_params(axis='y', colors='white')
    for spine in ax2.spines.values():
        spine.set_color("white")

    st.pyplot(fig2)

# ALBUM CHART
st.subheader("Top 10 Albums by Rating Count")

top_albums = df.sort_values(by=count_col, ascending=False).head(10)

fig3, ax3 = plt.subplots(figsize=(12, 5))
fig3.patch.set_facecolor("#0e1117")
ax3.set_facecolor("#0e1117")

album_colors = [colors[i % len(colors)] for i in range(len(top_albums))]
ax3.bar(top_albums[album_col], top_albums[count_col], color=album_colors)

ax3.set_title("Most Rated Albums", color="white")
ax3.tick_params(axis='x', rotation=45, colors='white')
ax3.tick_params(axis='y', colors='white')
for spine in ax3.spines.values():
    spine.set_color("white")

st.pyplot(fig3)

# ---- PREVIEW ----
with st.expander("Dataset Preview"):
    st.dataframe(df.head(20), use_container_width=True)
