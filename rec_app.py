import requests
import pickle
import pandas as pd
import time
from requests.adapters import HTTPAdapter, Retry
import streamlit as st 


movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies_dict_frame = pd.DataFrame(movies_dict)
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.header('🎬 Movie Recommender System')


session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retries))


def fetch_poster(movie_id):
    access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4NmJhMGRjNmJjZDcxZWI3NzQzMDMzMzQ0ZDliZmRmZiIsIm5iZiI6MTc2MTgyNjQ0MC45ODQsInN1YiI6IjY5MDM1Njg4MTMwZWQ1MzU4NzZiMzI0NSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lLZWfFNOiOL0-jBLjeOJ5NIWo2LA_jW4lKa1_KyBMFI"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"

    except requests.exceptions.RequestException as e:
        print(f"⚠ Network error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=Image+Unavailable"



def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
        time.sleep(0.2)  

    return recommended_movie_names, recommended_movie_posters



selected_by_user = st.selectbox('🎥 Select Your Choice', movies_dict_frame['title'].values)

if st.button('Show Recommendation'):
    movie_names, movie_posters = recommend(selected_by_user)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.subheader(movie_names[i])
            st.image(movie_posters[i])