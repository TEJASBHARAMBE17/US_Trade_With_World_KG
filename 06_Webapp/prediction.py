from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import pickle
import streamlit as st

class DataLoader:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
          self.driver.close()

    def load_test_data(self, country_id, fta_year):
        with self.driver.session(database="neo4j") as session:
            df = session.execute_write(self._load_test_data, country_id, 'From')
            df = pd.concat([df,
                            session.execute_write(self._load_test_data, country_id, 'To')]
                           , axis=0)
            df['fta_inforce'] = df['exports_year'].map(lambda x: 1 if x >= fta_year else 0)
            df['train'] = False
            return df
    
    @staticmethod
    def _load_test_data(tx, country_id, exported):
        seller_usa_dict = {'From':0, 'To':1}
        query = (
            "MATCH (year)<-[:tradedYear]-(trade) "
        )
        if exported == "From":
            query += ("MATCH (trade)-[:exportedFrom]->(country) ")
        else:
            query += ("MATCH (trade)-[:exportedTo]->(country) ")
        query +=(    
            "WHERE country.countryID=$country_id "
            "RETURN country.countryID as country_id, year.year as year, sum(trade.tradedValue) as value "
            "ORDER BY year"
        )
        result = tx.run(
            query, country_id=country_id
        )
        try:
            df = pd.DataFrame(
                [
                    [row["country_id"], seller_usa_dict[exported], row["year"], row["value"]]
                    for row in result
                ],
                columns=["trade_country", "seller_usa", "exports_year", "trade_value"],
            )
            return df
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

def get_X_y (train, test):
  df = pd.concat([train, test], axis=0)
  df_all = pd.concat([pd.get_dummies(df[['trade_country']].astype(str), drop_first=True),
               df[['seller_usa', 'fta_inforce', 'exports_year', 'train']]], axis=1)
  return df_all[df_all['train']==False].iloc[:,:-1]

def get_test_data(country_id, fta_year):
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    uri = "neo4j+s://43b50553.databases.neo4j.io"
    user = "neo4j"
    password = "zRFUl83bppdZqwmO1DFBaAxVGvZOct9LETZ_HXzJZNg"
    # uri = "neo4j+s://d85224fd.databases.neo4j.io"
    # user = "neo4j"
    # password = "xNNnI0kg_BP-4zM6pSB5k-aqA1PuChquxGgR0wooQSc"
    app = DataLoader(uri, user, password)

    df_train = pickle.load(open('../data/traindata.pkl','rb'))
    df_test = app.load_test_data(country_id, fta_year)
    X_test= get_X_y (df_train, df_test)

    app.close()
    return df_test, X_test

def show_prediction(df, pred, counter_country, fta_year):
    st.write('Prediction of Trade Value Change according to the year of FTA in-force')

    full = df[['seller_usa', 'exports_year', 'trade_value']].copy()
    full['pred'] = pred
    full['pred'] = full.apply(lambda x: x['pred'] if x['exports_year']>=fta_year else x['trade_value'], axis=1)
    full['status'] = 'Non-FTA'
    result = full[['seller_usa', 'exports_year', 'trade_value', 'status']]
    full['status'] = 'If FTA in Force'
    full['trade_value'] = full['pred'] 
    result = pd.concat([result, full[['seller_usa', 'exports_year', 'trade_value', 'status']]], axis=0)
    
    fig = px.line(result[result['seller_usa']==0], x='exports_year', y='trade_value', color='status', title='USA sells '+counter_country.upper()+' buys')
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.line(result[result['seller_usa']==1], x='exports_year', y='trade_value', color='status', title='USA buys '+counter_country.upper()+' sells')
    st.plotly_chart(fig, use_container_width=True)