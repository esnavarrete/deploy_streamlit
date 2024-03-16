import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Leyendo las credenciales para acceder a la DB
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)

# Función que lee la DB de firestore


@st.cache
def get_data_from_firestore():
    """ Función que lee todos los registros de Firestore en un dataframe """
    db = firestore.Client(credentials=creds, project="movies-challenge-ebf15")
    movies_ref = list(db.collection('movies').stream())
    movies_dicts = list(map(lambda x: x.to_dict(), movies_ref))
    data = pd.DataFrame(movies_dicts)
    return data


movies_df = get_data_from_firestore()

# -------------------------- Inicia la aplicación ---------------------------------------
st.title('Netflix App')

# Checkbox para mostrar todo el dataframe
show_data = st.sidebar.checkbox('Mostrar todos los filmes')
if show_data:
    st.header('Todos los filmes')
    st.dataframe(movies_df)
st.sidebar.markdown('----------')

# Búsqueda de filmes
st.sidebar.write('Búsqueda por nombre')
movie_name = st.sidebar.text_input('Título del filme:')
get_movies = st.sidebar.button('Buscar filmes')
if get_movies and movie_name:
    movies_found = movies_df[movies_df['name'].str.contains(
        movie_name, case=False)]
    st.write(f'Filmes encontrados: {len(movies_found)}')
    st.dataframe(movies_found)
st.sidebar.markdown('----------')

# Filtro por directores
st.sidebar.write('Filtrar por directores')
director_name = st.sidebar.selectbox(
    'Seleccione director:',
    movies_df['director'].unique())
get_movies_by_director = st.sidebar.button('Filtrar')
if get_movies_by_director and director_name:
    movies_found = movies_df[movies_df['director'] == director_name]
    st.write(f'Filmes encontrados: {len(movies_found)}')
    st.dataframe(movies_found)
st.sidebar.markdown('-----------')

# Insertar nuevo filme
st.sidebar.write('Insertar nuevo filme')
name = st.sidebar.text_input('Name:')
company = st.sidebar.text_input('Company:')
director = st.sidebar.text_input('Director:')
genre = st.sidebar.selectbox(
    'Genre:',
    movies_df['genre'].unique())
submit = st.sidebar.button('Crear nuevo filme')

if all([name, company, director, genre, submit]):
    db = firestore.Client(credentials=creds, project="movies-challenge-ebf15")
    doc_ref = db.collection('movies').document(name)
    doc_ref.set({
        'name': name,
        'company': company,
        'director': director,
        'genre': genre
    })
    st.sidebar.write('Filme agregado correctamente!')
