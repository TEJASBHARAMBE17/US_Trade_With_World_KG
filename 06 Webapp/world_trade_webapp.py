import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Overview",
        "Data viz with recommendation system",
        "Q&A with KG",
        "Prediction of world trade using KG",
    ]
)
with tab1:
    st.header("Overview")

with tab2:
    st.header("Data viz with recommendation system")

    with st.form("my_form"):

        counter_country = st.selectbox(
            "Counter Country", ("China", "South Korea", "India")
        )

        start_year, end_year = st.select_slider(
            "Select Year",
            options=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
            value=(2010, 2018),
        )

        product_selected = st.selectbox("Product", ("Rice", "Mobile", "Books"))

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(counter_country, start_year, end_year, product_selected)


with tab3:
    st.header("Q&A with the world trade KG")

with tab4:
    st.header("Prediction of world trade using KG")
