import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Music Stats Dashboard", layout="wide")

# Dark theme styling
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

# Load CSV
df = pd.read_csv("rym_clean1.csv")
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

# Fixed column names from your dataset
album_col = "release_name"
artist_col = "artist_name"
genre_col_1 = "primary_genres"
genre_col_2 = "secondary_genres"
rating_col = "avg_rating"
count_col = "rating_count"

# Clean empty values
df[genre_col_1] = df[genre_col_1].fillna("")
df[genre_col_2] = df[genre_col_2].fillna("")
df[artist_col] = df[artist_col].fillna("Unknown")
df[album_col] = df[album_col].fillna("Unknown")

# ---- Top statistics ----
best_rated_album = df.sort_values(by=[rating_col, count_col], ascending=[False, False]).iloc[0]
most_rated_album = df.sort_values(by=count_col, ascending=False).iloc[0]
most_rated_artist = df.groupby(artist_col)[count_col].sum().sort_values(ascending=False).iloc[0:1]
top_artist_name = most_rated_artist.index[0]
top_artist_count = int(most_rated_artist.iloc[0])

# Genre count from both columns
genres = pd.concat([
    df[genre_col_1].astype(str),
    df[genre_col_2].astype(str)
], ignore_index=True)

genre_list = (
    genres.str.split(",")
    .explode()
    .str.strip()
)

genre_list = genre_list[genre_list.notna() & (genre_list != "") & (genre_list != "nan")]
most_popular_genre = genre_list.value_counts().head(10)
top_genre = most_popular_genre.index[0]
top_genre_count = int(most_popular_genre.iloc[0])

# ---- KPI cards ----
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Best Rated Album", f"{best_rated_album[album_col]}", f"{best_rated_album[rating_col]:.2f}")
    st.caption(best_rated_album[artist_col])
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Most Popular Genre", top_genre, f"{top_genre_count} mentions")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Most Rated Artist", top_artist_name, f"{top_artist_count:,} ratings")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Most Rated Album", most_rated_album[album_col], f"{int(most_rated_album[count_col]):,} ratings")
    st.caption(most_rated_album[artist_col])
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ---- Charts ----
left, right = st.columns(2)

with left:
    st.subheader("Top 10 Genres")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    fig1.patch.set_facecolor("#0e1117")
    ax1.set_facecolor("#0e1117")
    most_popular_genre.plot(kind="bar", ax=ax1, color="#4ea1ff")
    ax1.set_xlabel("")
    ax1.set_ylabel("Count", color="white")
    ax1.tick_params(axis="x", rotation=45, colors="white")
    ax1.tick_params(axis="y", colors="white")
    ax1.set_title("Most Popular Genres", color="white")
    for spine in ax1.spines.values():
        spine.set_color("white")
    st.pyplot(fig1)

with right:
    st.subheader("Top 10 Artists by Rating Count")
    top_artists = df.groupby(artist_col)[count_col].sum().sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    fig2.patch.set_facecolor("#0e1117")
    ax2.set_facecolor("#0e1117")
    top_artists.plot(kind="bar", ax=ax2, color="#7cdb7c")
    ax2.set_xlabel("")
    ax2.set_ylabel("Ratings", color="white")
    ax2.tick_params(axis="x", rotation=45, colors="white")
    ax2.tick_params(axis="y", colors="white")
    ax2.set_title("Most Rated Artists", color="white")
    for spine in ax2.spines.values():
        spine.set_color("white")
    st.pyplot(fig2)

st.subheader("Top 10 Albums by Rating Count")
top_albums = df.sort_values(by=count_col, ascending=False).head(10)

fig3, ax3 = plt.subplots(figsize=(12, 5))
fig3.patch.set_facecolor("#0e1117")
ax3.set_facecolor("#0e1117")
ax3.bar(top_albums[album_col], top_albums[count_col], color="#ffb347")
ax3.set_xlabel("")
ax3.set_ylabel("Ratings", color="white")
ax3.tick_params(axis="x", rotation=45, colors="white")
ax3.tick_params(axis="y", colors="white")
ax3.set_title("Most Rated Albums", color="white")
for spine in ax3.spines.values():
    spine.set_color("white")
st.pyplot(fig3)

with st.expander("See dataset preview"):
    st.dataframe(df.head(20), use_container_width=True)
