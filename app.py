import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("novels1.csv")
    return df

novels1 = load_data()

# Label Encoding
le_genre = LabelEncoder()
le_title = LabelEncoder()
le_author = LabelEncoder()
le_status = LabelEncoder()

novels1['genre_encoded'] = le_genre.fit_transform(novels['genres'])
novels1['title_encoded'] = le_title.fit_transform(novels['title'])
novels1['author_encoded'] = le_author.fit_transform(novels['authors'])
novels1['status_encoded'] = le_status.fit_transform(novels['status'])

# Model untuk prediksi berdasarkan rating
X_rating = novels1[['genre_encoded', 'author_encoded', 'status_encoded']]
y_rating = novels1['scored']
model_rating = RandomForestClassifier(n_estimators=100, random_state=42)
model_rating.fit(X_rating, y_rating)

# Model untuk prediksi berdasarkan genre
X_genre = novels1[['scored', 'author_encoded', 'status_encoded']]
y_genre = novels1['genre_encoded']
model_genre = RandomForestClassifier(n_estimators=100, random_state=42)
model_genre.fit(X_genre, y_genre)

# Inisialisasi halaman
st.set_page_config(page_title="Novel Recommendation App", layout="wide")
page = st.sidebar.selectbox("Navigasi", ["Home", "Rekomendasi Berdasarkan Rating", "Rekomendasi Berdasarkan Genre"])

# Riwayat rekomendasi
if "history" not in st.session_state:
    st.session_state.history = []

# HOME PAGE
if page == "Home":
    st.title("📚 Beranda")

    st.subheader("10 Novel Paling Populer")
    top_popular = novels1.sort_values(by="popularty", ascending=False).head(10)
    st.dataframe(top_popular[['novel_id', 'title', 'authors', 'genres', 'scored', 'popularty']])

    st.subheader("Riwayat Rekomendasi")
    if st.session_state.history:
        for entry in st.session_state.history:
            st.markdown(f"**{entry['title']}** - {entry['type']}:")
            st.dataframe(entry['results'])
    else:
        st.write("Belum ada riwayat rekomendasi.")

# PAGE 2 - RATING
elif page == "Rekomendasi Berdasarkan Rating":
    st.title("⭐ Rekomendasi Berdasarkan Rating")
    selected_title = st.selectbox("Pilih judul novel", novels1['title'].unique())

    selected_row = novels1[novels1['title'] == selected_title].iloc[0]
    X_input = pd.DataFrame({
        'genre_encoded': [selected_row['genre_encoded']],
        'author_encoded': [selected_row['author_encoded']],
        'status_encoded': [selected_row['status_encoded']]
    })

    y_pred = model_rating.predict(X_input)[0]
    result = novels1[novels1['scored'] == y_pred].sort_values(by='popularty', ascending=False).head(10)

    st.write(f"Rekomendasi novel berdasarkan rating dari \"{selected_title}\":")
    st.dataframe(result[['novel_id', 'title', 'authors', 'genres', 'scored', 'popularty']])

    st.session_state.history.append({"title": selected_title, "type": "Rating", "results": result[['novel_id', 'title', 'authors', 'genres', 'scored', 'popularty']]})

# PAGE 3 - GENRE
elif page == "Rekomendasi Berdasarkan Genre":
    st.title("🎯 Rekomendasi Berdasarkan Genre")
    selected_title = st.selectbox("Pilih judul novel", novels['title'].unique(), key='genre')

    selected_row = novels[novels['title'] == selected_title].iloc[0]
    X_input = pd.DataFrame({
        'scored': [selected_row['scored']],
        'author_encoded': [selected_row['author_encoded']],
        'status_encoded': [selected_row['status_encoded']]
    })

    y_pred = model_genre.predict(X_input)[0]
    genre_name = le_genre.inverse_transform([y_pred])[0]
    result = novels[novels['genres'] == genre_name].sort_values(by='scored', ascending=False).head(10)

    st.write(f"Rekomendasi novel berdasarkan genre dari \"{selected_title}\" (Genre: {genre_name}):")
    st.dataframe(result[['novel_id', 'title', 'authors', 'genres', 'scored', 'popularty']])

    st.session_state.history.append({"title": selected_title, "type": "Genre", "results": result[['novel_id', 'title', 'authors', 'genres', 'scored', 'popularty']]})
