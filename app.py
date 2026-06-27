import pickle
import streamlit as st
import requests
import pandas as pd

def elegir_poster(movie_id):
    #url = "https://api.themoviedb.org/3/movie/{}api_key=23117a9ad724f3fbde01d284edd2291d&language=en-US".format(movie_id)
    url = "https://api.themoviedb.org/3/movie/{}?api_key=23117a9ad724f3fbde01d284edd2291d&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recomendarPelicula(nuevaPeliculas, similaridad, movie):
    index = nuevaPeliculas[nuevaPeliculas['title'] == movie].index[0]
    distancias = sorted(list(enumerate(similaridad[index])),reverse=True,key = lambda x: x[1])

    nombresPeliculasRecomendadas = []
    postersPeliculasRecomendadas = []

    for i in distancias[1:6]:
        movie_id = nuevaPeliculas.iloc[i[0]].movie_id
        nombresPeliculasRecomendadas.append(nuevaPeliculas.iloc[i[0]].title)
        postersPeliculasRecomendadas.append(elegir_poster(movie_id))

    return nombresPeliculasRecomendadas, postersPeliculasRecomendadas

def main():
    st.header("Sistema de Recomendación de Películas")
    nuevaPeliculas = pd.read_pickle('peliculas.pkl')
    similaridad = pd.read_pickle('similaridad.pkl')

    listaPeliculas = nuevaPeliculas['title'].values
    peliculaSeleccionada = st.selectbox(
        "Selecciona película:",
        listaPeliculas
    )

    if st.button("Recomendarme películas similares:"):
        nombresPeli, postersPeli = recomendarPelicula(nuevaPeliculas, similaridad, peliculaSeleccionada)

        cols = st.columns(5)

        for i, col in enumerate(cols):
            col.text(nombresPeli[i])
            col.image(postersPeli[i])

if __name__ == "__main__":
    main()