from ast import If
from cProfile import label
from jmespath import search
import streamlit.components.v1 as stc
import streamlit as st
import requests
import pandas as pd
from tables import Col

# for grid of datas
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

# url from my api_Flask
base_url = "http://192.168.1.19:5001/"
base_url_search = "http://192.168.1.19:5001/{}"

# template for result of search
HTML_TEMPLATE_SEARCH = """
<div>
    <h4>{}</h4>
    <h6>{}</h6>
</div>
"""
HTML_TEMPLATE_SEARCH_DESC = """
<div style='color:#fff>
    {}
    {}
    {}
    {}
</div>
"""
HTML_TEMPLATE_VIEW = """
<div style='color:#fff>
    {}
    {}
    {}
    {}
    {}
    {}
    <p>---------------</p>
</div>
"""
###
#fonction qui return un json pour les parametres a mettre dans les requetes
param_data_base = {
  "database": "db_movies",
  "collection": "top"
}

def get_data(url):
    resp = requests.get(url,data=param_data_base)
    return resp


def add_movie(url, titre, real, acteurs, genre, date, dure):
    data_add = param_data_base["Document"] = {titre, real, acteurs, genre, date, dure}
    resp = requests.post(url, data=data_add)
    return resp.json()


def uptade_movie(url,movie_to_update,data_to_update):
    data_up = param_data_base["Filter"] = {movie_to_update}
    data_up["DataToBeUpdated"]={data_to_update}
    resp = requests.put(url,data=data_up)
    return resp.json()


def delete_movie(url,movie_to_delete):
    data_delete = param_data_base["Filter"] = {movie_to_delete}
    resp = requests.delete(url,data=data_delete)
    return resp.json()


def get_all_title(url):
    resp = requests.get(url+"all_titles",data=param_data_base)
    return resp.json()


def get_movie_by_title(url,title):
    resp = requests.get(base_url+"find_by_title",data=title)
    return resp.json()


def main():
    st.title("TOP 100 MOVIE IN ALLOCINE")

    menu = ["Home", "Add movie", "Remove movie",
            "Update movie", "Search movie", "Visualisation DF"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

        data = get_data(base_url+"/shows_datas")
        st.write(data)
        for i in data:
                movie_title = i[0]
                movie_real = i[1]
                movie_acteurs = i[2]
                movie_genre = i[3]
                movie_date = i[4]
                movie_dure = i[5]
                st.markdown(HTML_TEMPLATE_VIEW.format(movie_title, movie_real, movie_acteurs,movie_genre,movie_date,movie_dure ),
                            unsafe_allow_html=True)
        # exemple:{'col1': [1, 2, 3], 'col2': [4, 5, 6]}
        #df = pd.DataFrame(data)
        #AgGrid(df)

    elif choice == "Add movie":
        st.subheader("add movie")

        movie_title = st.text_input("Entrez le titre du film", max_chars=50)
        movie_real = st.text_input(
            "Entrez le nom du réalisateur", max_chars=50)
        movie_acteurs = st.text_input(
            "Entrez le nom des acteurs principaux")
        movie_genre = st.text_input("Entrez le nom du genre")
        movie_date = st.date_input("Entrez la date de sortie en salle")
        movie_dure = st.text_input("Entrez le durée du film", max_chars=50)

        if st.button("Add"):
            # appeler la fonction (avec les varioubles au dessus) ajout movie qui va faire le lien avec l'api
            st.success("Post:{} saved".format(movie_title))

    elif choice == "Remove movie":
        st.subheader("remove movie")

        # liste tous les titres sur la bare de menu gauche
        all_title = get_all_title(base_url+"all_titles")
        st.write(all_title)
        movie_to_delete = st.selectbox("Title of movies", all_title)

        if st.button("Delete"):
            # appeler la fonction (avec movie_to_delete) ajout movie qui va faire le lien avec l'api
            st.success("Post:{} delete".format(movie_to_delete))

    elif choice == "Update movie":
        st.subheader("Update movie")

        # liste tous les titres sur la bare de menu gauche
        all_title = get_all_title(base_url)
        movies_target = st.sidebar.selectbox("Title of movies", all_title)
        # recupere le titre que je veux supprimer
        movie_filter_result = get_movie_by_title(base_url,movies_target)

        movie_title = st.text_input(
            "Entrez le titre du film", value=movie_filter_result[0], max_chars=50)
        movie_real = st.text_input(
            "Entrez le nom du réalisateur", value=movie_filter_result[1], max_chars=50)
        movie_acteurs = st.text_input("Entrez le nom des acteurs principaux",
                                      value=movie_filter_result[2], height=100)
        movie_genre = st.text_input(
            "Entrez le nom du genre", value=movie_filter_result[3])
        movie_date = st.date_input("Entrez la date de sortie en salle",
                                   value=movie_filter_result[4])
        movie_dure = st.text_input(
            "Entrez le durée du film", value=movie_filter_result[5], max_chars=50)

        if st.button("Update"):
            # appeler la fonction (avec les varioubles au dessus) ajout movie qui va faire le lien avec l'api
            st.success("Post:{} saved".format(movie_title))

    elif choice == "Search movie":
        st.subheader("search movie")

        with st.form(key="searchform"):
            nav1, nav2 = st.columns([2, 1])
            with nav1:
                search_title = st.text_input("Search title")
            with nav2:
                st.text("Search ")
                submit_search = st.form_submit_button(label='Search')
            st.success("You searched the movie {}".format(search_title))

            # result of the search
            col1 = st.columns([1])
            with col1:
                if submit_search:
                    data = get_movie_by_title(base_url,search_title)
                    num_of_result = len(data)
                    st.subheader("showing {} movies".format(num_of_result))

                    for i in data:
                        movie_title_search = i['Titre']
                        movie_real_search = i['Réalisateur']
                        movie_acteurs_search = i['Acteurs principaux']
                        movie_genre_search = i['Genre']
                        movie_date_search = i['Date de parution en salle']
                        movie_dure_search = i['Durée']
                        st.markdown(HTML_TEMPLATE_SEARCH.format(movie_title_search, movie_real_search),
                                    unsafe_allow_html=True)

                        # description
                        with st.beta_expander("Plus d'infos"):
                            st.html(HTML_TEMPLATE_SEARCH_DESC.format(
                                movie_acteurs_search, movie_genre_search, movie_date_search, movie_dure_search), scrolling=True)

    elif choice == "Visualisation":
        st.subheader("Visualisation of my data")

        movies = pd.read_excel("src\output.xlsx")  

        def aggrid_interactive_table(df: pd.DataFrame):

            options = GridOptionsBuilder.from_dataframe(
                df, enableValue=True, enablePivot=True
            )

            options.configure_side_bar()

            options.configure_selection("single")
            selection = AgGrid(
                df,
                enable_enterprise_modules=True,
                gridOptions=options.build(),
                theme="light",
                update_mode=GridUpdateMode.MODEL_CHANGED,
                allow_unsafe_jscode=True,
            )

            return selection


        movies = pd.read_excel("src\output.xlsx")  

        selection = aggrid_interactive_table(df=movies)

        if selection:
            st.write("You selected:")
            st.json(selection["selected_rows"])

if __name__ == '__main__':
    main()
