from transformers import pipeline
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import pandas as pd
import numpy as np
from neo4j.exceptions import Neo4jError
import rltk
import spacy
import streamlit as st

nlp = spacy.load("en_core_web_sm")


def extract_entities(question):
    doc = nlp(question)
    gpe_entities = []
    date_entities = []
    for ent in doc.ents:
        if ent.label_ == "GPE":
            gpe_entities.append(ent.text)
        if ent.label_ == "DATE":
            date_entities.append(ent.text)

    nsubj_enitities = []
    dobj_enitities = []
    for token in doc:
        if token.dep_ == "nsubj":
            nsubj_enitities.append(token.text)
        if token.dep_ == "dobj":
            dobj_enitities.append(token.text)
    return gpe_entities, date_entities, nsubj_enitities, dobj_enitities


def country_similarity(r1, r2):
    """Example dummy similiary function"""
    s1 = r1.lower()
    s2 = r2.lower()

    sim1 = rltk.jaro_winkler_similarity(s1, s2)
    sim2 = rltk.dice_similarity(set(s1), set(s2))
    return 0.7 * sim1 + 0.3 * sim2


def product_similarity(r1, r2):
    """Example dummy similiary function"""
    s1 = r1.lower()
    s2 = r2.lower()

    sim1 = rltk.jaro_winkler_similarity(s1, s2)
    sim2 = rltk.dice_similarity(set(s1), set(s2))
    return 0.7 * sim1 + 0.3 * sim2


def find_the_matching_country(dict_country, match_country):
    track_score = dict()
    for eachCountry in dict_country.values():
        track_score[(match_country, eachCountry)] = country_similarity(
            eachCountry, match_country
        )

    return dict(sorted(track_score.items(), key=lambda item: item[1], reverse=True))


def find_the_matching_product(truth_product_list, match_product):
    track_score = dict()
    for eachCountry in truth_product_list:
        track_score[(match_product, eachCountry)] = country_similarity(
            eachCountry, match_product
        )
    return dict(sorted(track_score.items(), key=lambda item: item[1], reverse=True))


def get_gdp_details(buyer, processed_year, app, dict_country, dict_country_rev):
    generated_gdp = ""
    output_5 = pd.DataFrame(
        app.country(buyer),
        columns=[
            "Name",
            "Population",
            "gdp_2020",
            "gdp_2019",
            "gdp_2018",
            "gdp_2017",
            "gdp_2016",
            "gdp_2015",
            "gdp_2014",
            "gdp_2013",
            "gdp_2012",
            "gdp_2011",
            "gdp_2010",
        ],
    )
    for i, text in output_5.iterrows():
        generated_gdp += (
            text["Name"]
            + " has population of "
            + str(text["Population"])
            + ". "
            + text["Name"]
            + " had GDP of $"
            + str(text["gdp_2020"] / 1000000000)
            + "B in 2020 "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2019"] / 1000000000)
            + "B in 2019. "
            + text["Name"]
            + " had GDP of $"
            + str(text["gdp_2018"] / 1000000000)
            + "B in 2018. "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2017"] / 1000000000)
            + "B in 2017. "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2016"] / 1000000000)
            + "B in 2016. "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2015"] / 1000000000)
            + "B in 2015. "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2014"] / 1000000000)
            + "B in 2014. "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2013"] / 1000000000)
            + "B in 2013. "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2012"] / 1000000000)
            + "B in 2012. "
            + text["Name"]
            + "B had GDP of $"
            + str(text["gdp_2011"] / 1000000000)
            + "B in 2011. "
            + text["Name"]
            + " had GDP of $"
            + str(text["gdp_2010"] / 1000000000)
            + "B in 2010. "
        )
    return generated_gdp


def generate_c2c_trades(
    buyer, seller, processed_year, app, dict_country, dict_country_rev
):
    generated_c2c_trades = ""
    output_3 = pd.DataFrame(
        app.c2c_products_year(buyer, seller), columns=["Year", "Section"]
    )

    for year in list(output_3["Year"].unique()):
        line = []
        if year == processed_year:
            for text in output_3[output_3["Year"] == year]["Section"]:
                line.append(text)
            generated_c2c_trades += (
                " In "
                + str(year)
                + ", "
                + dict_country[buyer]
                + " exported the following products from "
                + dict_country[seller]
                + ":  "
                + ",".join(str(item) for item in line)
                + "."
            )

    output_1 = pd.DataFrame(
        app.c2c_trade(buyer, seller), columns=["Buyer", "Seller", "Worth", "Year"]
    )
    for i, text in output_1.iterrows():
        if text["Year"] == processed_year:
            generated_c2c_trades += (
                " "
                + text["Buyer"]
                + " exported from "
                + text["Seller"]
                + " worth $"
                + str(text["Worth"])
                + " in "
                + str(text["Year"])
                + "."
            )

    output_4 = pd.DataFrame(
        app.c2c_trade_product(buyer, seller),
        columns=["Buyer", "Seller", "Worth", "Product", "Year"],
    )
    for i, text in output_4.iterrows():
        if text["Year"] == processed_year:
            generated_c2c_trades += (
                " "
                + text["Buyer"]
                + " exported "
                + text["Product"]
                + " from "
                + text["Seller"]
                + " worth $"
                + str(text["Worth"])
                + " in "
                + str(text["Year"])
                + "."
            )

    return generated_c2c_trades


def generate_products(app, dict_country, dict_country_rev):
    output_6 = pd.DataFrame(app.product_hierarchy(), columns=["Section", "Category"])
    generated_products = ""
    for section in list(output_6["Section"].unique()):
        line = []
        for text in output_6[output_6["Section"] == section]["Category"]:
            line.append(text)
        generated_products += (
            " " + section + " contains " + ", ".join(str(item) for item in line) + "."
        )
    return generated_products


def generate_FTA(app, dict_country, dict_country_rev):
    output_7 = pd.DataFrame(app.FTA(), columns=["Country"])
    generated_FTAs = ""
    output_7 = output_7[output_7["Country"] != "United States"]
    print(output_7["Country"].unique())

    line = []
    for c in list(output_7["Country"].unique()):
        line.append(c)
    generated_FTAs += (
        " " + "USA has FTA with " + ", ".join(str(item) for item in line) + "."
    )
    return generated_FTAs


def generate_country_trades(buyer, processed_year, app, dict_country, dict_country_rev):
    generated_country_trades = ""
    output_7 = pd.DataFrame(
        app.c_trade(buyer), columns=["Buyer", "Seller", "Worth", "Year"]
    )
    country_sellers = set()
    for i, text in output_7.iterrows():
        if text["Year"] == processed_year:
            country_sellers.add(text["Seller"])
            generated_country_trades += (
                " "
                + text["Buyer"]
                + " exported from "
                + text["Seller"]
                + " worth $"
                + str(text["Worth"])
                + " in "
                + str(text["Year"])
                + "."
            )
    generated_country_trades += (
        " "
        + dict_country[buyer]
        + " trades with "
        + ", ".join(str(item) for item in list(country_sellers))
        + "."
    )
    return generated_country_trades


def question_answer(question, app, dict_country, dict_country_rev):
    gpe, date, nsubj, dobj = extract_entities(question)
    # print("\n",gpe,date,nsubj,dobj)
    products = pd.read_csv("../data/products.csv")
    truth_product_list = list(products["section_name"].unique())
    question_dict = dict()
    # st.warning("Peforming the following step: Entity Recognition")
    for country in gpe:
        list_c = find_the_matching_country(dict_country, country)
        question_dict[list(list_c)[0][0]] = dict_country_rev[list(list_c)[0][1]].split(
            "_"
        )[0]

    if date != []:
        processed_year = pd.DataFrame(date, columns=["date"])
        processed_year["date"] = pd.to_datetime(processed_year["date"])
        processed_year = processed_year["date"].dt.year
        question_dict[date[0]] = processed_year[0]
        processed_year = processed_year[0]

    for subj in nsubj:
        if subj not in question_dict.keys():
            if "GDP" not in subj and "product" not in subj:
                list_p = find_the_matching_product(truth_product_list, subj)
                question_dict[list(list_p)[0][0]] = list(list_p)[0][1]
            else:
                question_dict[subj] = subj.lower()

    # st.warning(
    #     "Peforming the following step: Updating the question with entities found"
    # )
    for word, initial in question_dict.items():
        question = question.replace(word, str(initial))
    print("Updated_question: ", question)

    qa_model = pipeline("question-answering")
    if len(gpe) > 1:
        # st.warning("Peforming the following step: Generating Context")
        context = generate_c2c_trades(
            question_dict[gpe[0]],
            question_dict[gpe[1]],
            processed_year,
            app,
            dict_country,
            dict_country_rev,
        )
        print(1)
        # st.warning(
        #     "Peforming the following step: Answering with the https://huggingface.co/distilbert-base-cased-distilled-squad"
        # )
        if "product" in question.lower():
            return (
                question,
                context,
                qa_model(question=question, context=context, top_k=5),
            )
        else:
            return question, context, qa_model(question=question, context=context)

    elif "gdp" in question.lower():
        # st.warning("Peforming the following step: Generating Context")
        context = get_gdp_details(
            question_dict[gpe[0]],
            processed_year,
            app,
            dict_country,
            dict_country_rev,
        )
        print(2)
        # st.warning(
        #     "Peforming the following step: Answering with the https://huggingface.co/distilbert-base-cased-distilled-squad"
        # )
        return question, context, qa_model(question=question, context=context)

    elif "fta" in question.lower():
        # st.warning("Peforming the following step: Generating Context")
        context = generate_FTA(app, dict_country, dict_country_rev)
        print(3)
        # st.warning(
        #     "Peforming the following step: Answering with the https://huggingface.co/distilbert-base-cased-distilled-squad"
        # )
        return question, context, qa_model(question=question, context=context, top_k=10)

    elif (
        "contain" in question.lower()
        or "include" in question.lower()
        or "compromise" in question.lower()
    ):
        # st.warning("Peforming the following step: Generating Context")
        context = generate_products(app, dict_country, dict_country_rev)
        print(4)
        # st.warning(
        #     "Peforming the following step: Answering with the https://huggingface.co/distilbert-base-cased-distilled-squad"
        # )
        return question, context, qa_model(question=question, context=context, top_k=17)

    else:
        print(5)
        # st.warning("Peforming the following step: Generating Context")
        context = generate_country_trades(
            question_dict[gpe[0]],
            processed_year,
            app,
            dict_country,
            dict_country_rev,
        )
        # st.warning(
        #     "Peforming the following step: Answering with the https://huggingface.co/distilbert-base-cased-distilled-squad"
        # )
        return question, context, qa_model(question=question, context=context, top_k=3)


def get_country_dict():
    country_codes = pd.read_csv("../data/country_codes.csv")
    df2 = pd.DataFrame(
        {
            "iso_3": [
                "USA_1",
                "USA_2",
                "USA_3",
                "USA_4",
                "USA_5",
                "USA_6",
                "USA_7",
                "USA_8",
                "USA_9",
                "USA_10",
                "USA_11",
                "USA_12",
                "USA_13",
            ],
            "name": [
                "us",
                "US",
                "usa",
                "U.S.",
                "USA",
                "U. S.",
                "U.S.A.",
                "U. S. A.",
                "US of A",
                "U.S. of A",
                "U. S. of A",
                "United States",
                "United States of America",
            ],
        }
    )

    country_codes[country_codes["iso_3"] == "USA"]
    country_codes = (
        pd.concat([country_codes, df2]).reset_index().drop(columns=["index"])
    )
    dict_country = dict()
    for i, c in country_codes.iterrows():
        dict_country[c["iso_3"].lower()] = c["name"]
    dict_country_rev = dict()
    for key, value in dict_country.items():
        dict_country_rev[value] = key
    return dict_country, dict_country_rev


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def c_trade(self, p1):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_c_trade, p1)

    @staticmethod
    def fetch_c_trade(tx, p1):

        query1 = " MATCH (t1)-[r3:exportedFrom]->(c1) MATCH (t1)-[r4:exportedTo]->(c2) MATCH (t1)-[r1:tradedYear]->(y1) WHERE c1.countryID=$p1 return c1,c2,y1,sum(t1.tradedValue) as traded_val"

        result = tx.run(query1, p1=p1)
        try:
            return [
                [
                    record["c1"]["name"],
                    record["c2"]["name"],
                    record["traded_val"],
                    record["y1"]["year"],
                ]
                for record in result
            ]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise

    def c2c_trade(self, p1, p2):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_c2c_trade, p1, p2)

    @staticmethod
    def fetch_c2c_trade(tx, p1, p2):

        query1 = " MATCH (t1)-[r3:exportedFrom]->(c1) MATCH (t1)-[r4:exportedTo]->(c2) MATCH (t1)-[r1:tradedYear]->(y1) WHERE c1.countryID=$p1 AND c2.countryID=$p2 return c1,c2,y1,sum(t1.tradedValue) as traded_val"

        result = tx.run(
            query1,
            p1=p1,
            p2=p2,
        )
        try:
            return [
                [
                    record["c1"]["name"],
                    record["c2"]["name"],
                    record["traded_val"],
                    record["y1"]["year"],
                ]
                for record in result
            ]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise

    #########################################
    def c2c_trade_product(self, p1, p2):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_c2c_trade_product, p1, p2)

    @staticmethod
    def fetch_c2c_trade_product(tx, p1, p2):

        query1 = " MATCH (t1)-[r3:exportedFrom]->(c1) MATCH (t1)-[r4:exportedTo]->(c2) MATCH (t1)-[r1:tradedYear]->(y1) MATCH (t1)-[r2:tradedProduct]->(p1) WHERE c1.countryID=$p1 AND c2.countryID=$p2 return c1,c2,p1,sum(t1.tradedValue) as traded_val,y1.year as year"

        result = tx.run(query1, p1=p1, p2=p2)
        try:
            return [
                [
                    record["c1"]["name"],
                    record["c2"]["name"],
                    record["traded_val"],
                    record["p1"]["section"],
                    record["year"],
                ]
                for record in result
            ]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise

    def c2c_products(self, p1, p2):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_c2c_products, p1, p2)

    @staticmethod
    def fetch_c2c_products(tx, p1, p2):

        query1 = "MATCH (t1)-[r3:exportedFrom]->(c1) MATCH (t1)-[r4:exportedTo]->(c2) MATCH (t1)-[r2:tradedProduct]->(p1) WHERE c1.countryID=$p1 AND c2.countryID=$p2 return p1"

        result = tx.run(query1, p1=p1, p2=p2)
        try:
            return [[record["p1"]["section"]] for record in result]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise

    def c2c_products_year(self, p1, p2):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_c2c_products_year, p1, p2)

    @staticmethod
    def fetch_c2c_products_year(tx, p1, p2):

        query1 = "MATCH (t1)-[r3:exportedFrom]->(c1) MATCH (t1)-[r4:exportedTo]->(c2) MATCH (t1)-[r1:tradedYear]->(y1) MATCH (t1)-[r2:tradedProduct]->(p1) WHERE c1.countryID=$p1 AND c2.countryID=$p2 return y1,p1"

        result = tx.run(query1, p1=p1, p2=p2)
        try:
            return [
                [record["y1"]["year"], record["p1"]["section"]] for record in result
            ]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise

    def country(self, p1):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_country, p1)

    @staticmethod
    def fetch_country(tx, p1):

        query1 = "MATCH (c1:Country) where c1.countryID=$p1 return c1"
        result = tx.run(query1, p1=p1)
        try:
            return [
                [
                    record["c1"]["name"],
                    record["c1"]["population"],
                    record["c1"]["gdp_2020"],
                    record["c1"]["gdp_2019"],
                    record["c1"]["gdp_2018"],
                    record["c1"]["gdp_2017"],
                    record["c1"]["gdp_2016"],
                    record["c1"]["gdp_2015"],
                    record["c1"]["gdp_2014"],
                    record["c1"]["gdp_2013"],
                    record["c1"]["gdp_2012"],
                    record["c1"]["gdp_2011"],
                    record["c1"]["gdp_2010"],
                ]
                for record in result
            ]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise

    def product_hierarchy(self):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_product_hierarchy)

    @staticmethod
    def fetch_product_hierarchy(tx):

        query1 = "match (s1)<-[r1:hasSection]-(c1) return c1,s1"
        result = tx.run(query1)
        try:
            return [
                [record["s1"]["section"], record["c1"]["Category"]] for record in result
            ]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise

    def FTA(self):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self.fetch_FTA)

    @staticmethod
    def fetch_FTA(tx):

        query1 = "match (f1)-[r1:hasFTA]->(c1) where f1.has_fta=true return c1"
        result = tx.run(query1)
        try:
            return [[record["c1"]["name"]] for record in result]
        except Neo4jError as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query1, exception=exception
                )
            )
            raise


def q_a_main(question):
    # uri = "neo4j+s://2a05e02b.databases.neo4j.io"
    # user = "neo4j"
    # password = "tjWEIE9P86QZZqfpN-nKF7z-rfx1KD11OfNFQmoiFr0"
    uri = "neo4j+s://43b50553.databases.neo4j.io"
    user = "neo4j"
    password = "zRFUl83bppdZqwmO1DFBaAxVGvZOct9LETZ_HXzJZNg"
    app = App(uri, user, password)

    dict_country, dict_country_rev = get_country_dict()

    # question = "How much metals did USA export from China in 1st Jan 2010?"
    # question = "What was the GDP of United States in 2018?"
    # question = "What products did US export from China by 1st jan 2020?"
    # question = "What does Machine contain?"
    # question = "With whom does U.S trade?"
    # question = "With whom does U.S has FTA with?"

    print("Orginal Question: ", question)
    updated_ques, context, ans = question_answer(
        question, app, dict_country, dict_country_rev
    )
    try:
        df = pd.DataFrame(ans, index=[0])
        print(df)
    except:
        df = pd.DataFrame(ans)
        print(df)
    return updated_ques, context, df
