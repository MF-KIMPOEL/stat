import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Music Stats", layout="wide")

# ---- DARK STYLE ----
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🎧 Music Dataset Statistics")

# ---- LOAD DATA ----
df = pd.read_csv("rym_clean1.csv")

st.subheader("Dataset Preview")
st.write(df.head())

# ---- COLUMN AUTO-DETECTION (you can adjust if needed) ----
columns = df.columns.str.lower()

album_col = [c for c in df.columns if "album" in c.lower()][0]
artist_col = [c for c in df.columns if "artist" in c.lower()][0]
genre_col = [c for c in df.columns if "genre" in c.lower()][0]
rating_col = [c for c in df.columns if "rating" in c.lower()][0]

# ---- BEST RATED ALBUM ----
st.subheader("🏆 Best Rated Album")
best_album = df.sort_values(by=rating_col, ascending=False).iloc[0]
st.write(best_album[[album_col, artist_col, rating_col]])

# ---- MOST POPULAR GENRE ----
st.subheader("🔥 Most Popular Genre")
top_genre = df[genre_col].value_counts().head(10)

fig1, ax1 = plt.subplots()
ax1.set_facecolor("#0e1117")
fig1.patch.set_facecolor("#0e1117")

top_genre.plot(kind='bar', ax=ax1)
ax1.tick_params(colors='white')
ax1.set_title("Top Genres", color='white')

st.pyplot(fig1)

# ---- MOST RATED ARTIST ----
st.subheader("🎤 Most Rated Artist")
top_artist = df[artist_col].value_counts().head(10)

fig2, ax2 = plt.subplots()
ax2.set_facecolor("#0e1117")
fig2.patch.set_facecolor("#0e1117")

top_artist.plot(kind='bar', ax=ax2)
ax2.tick_params(colors='white')
ax2.set_title("Top Artists", color='white')

st.pyplot(fig2)

# ---- MOST RATED ALBUM ----
st.subheader("💿 Most Rated Album")
top_album = df[album_col].value_counts().head(10)

fig3, ax3 = plt.subplots()
ax3.set_facecolor("#0e1117")
fig3.patch.set_facecolor("#0e1117")

top_album.plot(kind='bar', ax=ax3)
ax3.tick_params(colors='white')
ax3.set_title("Top Albums", color='white')

st.pyplot(fig3)
