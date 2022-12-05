import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import streamlit.components.v1 as components
from PIL import Image
from st_clickable_images import clickable_images

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
    st.markdown("""""")
    st.subheader("International World Trade Exploration and Prediction:")
    # st.info(
    #     "Data Visualization: Use this tab to visualize the complex world trade easily"
    # )
    # st.info(
    #     "Q&A with KG: Use this tab to ask questions about the world trade to our app"
    # )
    # st.info("Prediction & Recommendation: Use this tab to predict the impact of FTA")
    # st.info("Neo4j Graph: View our KG here")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**Data Visualization**")
        st.image("../data/data_viz_img.png")

    with col2:
        st.markdown("**Q&A with KG**")
        st.image("../data/q_a_img.png")

    with col3:
        st.markdown("**Prediction & Recommendation**")
        st.image("../data/pred_img.png")

    with col4:
        st.markdown("**Neo4j Graph**")
        st.image("../data/neo4j_img.png")

    # image = Image.open("../data/globe2.jpeg")
    # st.image(image, caption="Ontology")
    st.markdown("""---""")
    st.subheader("About our platform:")

    st.markdown(
        "- **We have built a tool to visualize the complex world trade easily and also, aligned it with the country related metrics such as GDP/population.**"
    )
    st.markdown(
        "- **One can use this platform to ask questions about the world trade to our app and to predict the future trades between countries.**"
    )
    st.markdown(
        "- **The tool also recommends whether a country should go in FTA with some country or not and helps to predict the impact of FTA.**"
    )
    st.markdown(
        "- **Additionally, the data could also be queried and visualized using the Knowledge Graph that we built.**"
    )


with tab2:
    st.header("Data Visualization")

    country_dict = (
        pd.read_csv("../data/country_codes.csv").set_index("name").T.to_dict("list")
    )
    df_trades = pd.read_csv("../data/trades_v3_combined.csv")

    with st.form("form_visualization"):

        # col1, col2, col3, col4 = st.columns(4)
        col1, col2 = st.columns(2)

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

        # with col3:
        product_selected = st.selectbox("Product", df_trades["section_name"].unique())

        # with col4:
        st.write("")
        st.write("")
        submitted = st.form_submit_button("Submit")

        if submitted:
            counter_country = country_dict[counter_country.lower()][0].lower()
            start_year = start_year
            end_year = end_year
            product_selected = product_selected
            run_visualization(
                country_name, counter_country, start_year, end_year, product_selected
            )


with tab3:
    st.header("Q&A with the World Trade KG")
    st.write("Methodology to Answer the Questions")
    st.markdown("**Template Questions:**")
    st.info(
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
                "Select FTA Year to Predict Trade Value Change",
                options=[i for i in range(2010, 2021, 1)],
                value=2015,
            )

        submitted = st.form_submit_button("Submit")
        if submitted:
            country_id = country_id
            fta_year = fta_year

            estimator = pickle.load(open("../data/rf_2211261626.pkl", "rb"))

            df_test1, X_test1 = get_test_data(country_id, fta_year)
            show_prediction(
                df_test1, estimator.predict(X_test1), counter_country, fta_year
            )

            df_test2, X_test2 = make_test_X(country_id)
            df_addition = pd.concat(
                [
                    df_test1[
                        df_test1.apply(
                            lambda x: True
                            if x["seller_usa"] == 0
                            and x["Trade Year"] == df_test1["Trade Year"].max()
                            else False,
                            axis=1,
                        )
                    ],
                    df_test1[
                        df_test1.apply(
                            lambda x: True
                            if x["seller_usa"] == 1
                            and x["Trade Year"] == df_test1["Trade Year"].max()
                            else False,
                            axis=1,
                        )
                    ],
                ],
                axis=0,
            )
            show_later_years_prediction(
                df_test1,
                df_test2,
                df_addition,
                estimator.predict(X_test2),
                counter_country,
            )


with tab5:
    st.header("Neo4j graph")
    components.iframe(
        "https://browser.neo4j.io/?connectURL=neo4j%2Bs%3A%2F%2Fneo4j%4050728551.databases.neo4j.io%2F&_ga=2.81391250.408191067.1668294782-2032509330.1661934579",
        height=600,
    )
    image = Image.open("../data/ontology.png")

    st.image(image, caption="Ontology")
