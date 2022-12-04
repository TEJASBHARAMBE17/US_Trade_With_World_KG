import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import streamlit.components.v1 as components
from PIL import Image

# embed streamlit docs in a streamlit app

from VizApp import *
from q_a import *
from prediction import *

st.set_page_config(layout="wide")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Overview",
        "Data Visualization",
        "Q&A with KG",
        "Prediction & Recommendation",
        "Neo4j Graph",
    ]
)
with tab1:
    st.header("Overview")
    st.balloons()

    st.info(
        "Data Visualization: Use this tab to visualize the complex world trade easily"
    )
    st.info(
        "Q&A with KG: Use this tab to ask questions about the world trade to our app"
    )
    st.info("Prediction & Recommendation: Use this tab to predict the impact of FTA")
    st.info("Neo4j Graph: View our KG here")
    image = Image.open("../data/globe2.jpeg")
    st.image(image, caption="Ontology")

with tab2:
    st.header("Data Visualization")

    country_dict = (
        pd.read_csv("../data/country_codes.csv").set_index("name").T.to_dict("list")
    )
    df_trades = pd.read_csv("../data/trades_v3_combined.csv")

    with st.form("form_visualization"):

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            counter_country = st.selectbox(
                "Counter Country", [x.upper() for x in list(country_dict.keys())]
            )
            country_name = counter_country

        with col2:
            start_year, end_year = st.select_slider(
                "Select Year",
                options=[i for i in range(2010, 2021, 1)],
                value=(2010, 2018),
            )

        with col3:
            product_selected = st.selectbox("Product", df_trades["section_name"])

        with col4:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("Submit")

        if submitted:
            counter_country = country_dict[counter_country.lower()][0].lower()
            start_year = start_year
            end_year = end_year
            product_selected = product_selected
            # st.write(counter_country, start_year, end_year, product_selected)
            run_visualization(
                country_name, counter_country, start_year, end_year, product_selected
            )


with tab3:
    st.header("Q&A with the World Trade KG")
    st.write("Methodology to answer the questions")
    st.markdown("**Template Questions:**")
    st.warning(
        """\n
        What was the GDP of United States in 2018?\n
        What products did US export from China by 1st jan 2020?\n
        What does Machine contain?\n
        From whom did U.S export in 2020?\n
        With whom does U.S has FTA with?\n
        How much metals did USA export from China in 1st Jan 2010?\n
    """
    )

    with st.form("q_a_form"):

        question = st.text_input(
            "Enter the question", "With whom does U.S has FTA with?"
        )
        submitted_3 = st.form_submit_button("Submit")

        if submitted_3:
            updated_ques, context, ans = q_a_main(question)
            st.info("**Original question:** " + question + ":confetti_ball:")
            st.info("**Updated question:** " + updated_ques + ":confetti_ball:")
            st.info(
                "**Context generated to answer the question:** "
                + context[:1000]
                + ":confetti_ball:"
            )
            st.success("**Answer with scores:** ")
            st.table(ans)
with tab4:
    st.header("Prediction of world trade using KG")
    df_fta = pd.read_csv("../data/fta_pop_gdp_cleaned_v2.csv")[
        ["country", "country_code", "has_fta"]
    ]
    df_fta["country"] = df_fta["country"].map(lambda x: x.upper())

    with st.form("form_prediction"):

        col1, col2 = st.columns(2)

        with col1:
            country_id = st.selectbox(
                "Counter Country",
                df_fta[
                    df_fta.apply(
                        lambda x: False
                        if x["has_fta"] or x["country_code"] == "USA"
                        else True,
                        axis=1,
                    )
                ]["country"].map(lambda x: x.upper()),
            )
            counter_country = country_id
            country_id = (
                df_fta.reset_index(drop=True)
                .set_index("country")
                .T.to_dict("list")[country_id][0]
                .lower()
            )

        with col2:
            fta_year = st.select_slider(
                "Select Year", options=[i for i in range(2010, 2021, 1)], value=2015
            )

        submitted = st.form_submit_button("Submit")
        if submitted:
            country_id = country_id
            fta_year = fta_year

            df_test, X_test = get_test_data(country_id, fta_year)
            estimator = pickle.load(open("../data/rf_2211261626.pkl", "rb"))
            show_prediction(
                df_test, estimator.predict(X_test), counter_country, fta_year
            )

with tab5:
    st.header("Neo4j graph")
    components.iframe(
        "https://browser.neo4j.io/?connectURL=neo4j%2Bs%3A%2F%2Fneo4j%4050728551.databases.neo4j.io%2F&_ga=2.81391250.408191067.1668294782-2032509330.1661934579",
        height=600,
    )
    image = Image.open("../data/ontology.png")

    st.image(image, caption="Ontology")
