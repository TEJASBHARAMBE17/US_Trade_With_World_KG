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
    
    def get_new_years(self, country_id):
        with self.driver.session(database="neo4j") as session:
            df = session.execute_write(self._get_new_years, country_id, "From")
            df = pd.concat([df,
                            session.execute_write(self._get_new_years, country_id, "To")]
                           , axis=0)
            # df['fta_inforce'] = df['exports_year'].map(lambda x: 1 if x >= fta_year else 0)
            df['train'] = False
            return df
             

    @staticmethod
    def _get_new_years(tx, country_id, exported):
        seller_usa_dict = {'From':0, 'To':1}
        tf_dict = {True:1, False:0}
        query = (
            "MATCH (fta)-[:hasFTA]->(country)"
        )
        if exported == "From":
            query += ("MATCH (year)<-[:tradedYear]-(trade)-[:exportedFrom]->(country) ")
        else:
            query += ("MATCH (year)<-[:tradedYear]-(trade)-[:exportedTo]->(country) ")
        query +=( 
            "WHERE country.countryID=$country_id "
            "RETURN country.countryID as country_id, max(year.year) as year, fta.has_fta as fta_inforce "
        )
        result = tx.run(
            query, country_id=country_id
        )
        try:
            df = pd.DataFrame(
                [
                    [row["country_id"], seller_usa_dict[exported], row["year"]+1, 0, tf_dict[row["fta_inforce"]]]
                    for row in result
                ],
                columns=["trade_country", "seller_usa", "exports_year", "trade_value", "fta_inforce"],
            )
            return df
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

def get_X_test (train, test):
  df = pd.concat([train, test], axis=0)
  df_all = pd.concat([pd.get_dummies(df[['trade_country']].astype(str), drop_first=True),
               df[['seller_usa', 'fta_inforce', 'exports_year', 'train']]], axis=1)
  return df_all[df_all['train']==False].iloc[:,:-1]


def get_test_data(country_id, fta_year):
    uri = "neo4j+s://43b50553.databases.neo4j.io"
    user = "neo4j"
    password = "zRFUl83bppdZqwmO1DFBaAxVGvZOct9LETZ_HXzJZNg"
    app = DataLoader(uri, user, password)

    df_train = pickle.load(open('../data/traindata.pkl','rb'))
    df_test = app.load_test_data(country_id, fta_year)
    X_test= get_X_test (df_train, df_test)
    
    app.close()
    return df_test, X_test

def show_prediction(df, pred, counter_country, fta_year):
    full = df[['seller_usa', 'exports_year', 'trade_value']].copy()
    full['pred'] = pred
    full['pred'] = full.apply(lambda x: x['pred'] if x['exports_year']>=fta_year else x['trade_value'], axis=1)
    full['status'] = 'Non-FTA (history)'
    result = full[['seller_usa', 'exports_year', 'trade_value', 'status']]
    full['status'] = 'If FTA in Force (prediction)'
    full['trade_value'] = full['pred'] 
    result = pd.concat([result, full[['seller_usa', 'exports_year', 'trade_value', 'status']]], axis=0)
    result = result[result['trade_value']!=0]

    us_sells_history = result[result.apply(lambda x: True if x['status']=='Non-FTA (history)' and x['seller_usa']==1 and x['exports_year']>=fta_year else False, axis=1)]['trade_value'].mean()
    us_sells_predict = result[result.apply(lambda x: True if x['status']!='Non-FTA (history)' and x['seller_usa']==1 and x['exports_year']>=fta_year else False, axis=1)]['trade_value'].mean()
    us_buys_history = result[result.apply(lambda x: True if x['status']=='Non-FTA (history)' and x['seller_usa']==0 and x['exports_year']>=fta_year else False, axis=1)]['trade_value'].mean()
    us_buys_predict = result[result.apply(lambda x: True if x['status']!='Non-FTA (history)' and x['seller_usa']==0 and x['exports_year']>=fta_year else False, axis=1)]['trade_value'].mean()

    if (us_sells_predict - us_sells_history) - (us_buys_predict - us_buys_history) > 0:
        st.write('Recommendation for USA: FTA with ' + counter_country)
    else:
        st.write('Recommendation for USA: No FTA with ' + counter_country)
    st.write('')
    st.write(f'What if FTA has been in force between USA and {counter_country} since {fta_year}')

    fig = px.line(result[result['seller_usa']==1], x='exports_year', y='trade_value', color='status', title='USA sells '+counter_country.upper()+' buys')
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.line(result[result['seller_usa']==0], x='exports_year', y='trade_value', color='status', title='USA buys '+counter_country.upper()+' sells')
    st.plotly_chart(fig, use_container_width=True)


def make_test_data (df):
    df = df.append([df]*1,ignore_index=True)
    year_from = df.loc[0, "exports_year"]
    year_to = df.loc[1, "exports_year"]
    df["exports_year"] = [year_from, year_to, year_from+1, year_to+1]
    return df

def make_test_X(country_id):
    uri = "neo4j+s://43b50553.databases.neo4j.io"
    user = "neo4j"
    password = "zRFUl83bppdZqwmO1DFBaAxVGvZOct9LETZ_HXzJZNg"
    app = DataLoader(uri, user, password)

    df_train = pickle.load(open('../data/traindata.pkl','rb'))
    df_last_year = app.get_new_years(country_id)    
    df_test = make_test_data (df_last_year)
    X_test= get_X_test (df_train, df_test)

    app.close()
    return df_test, X_test

def show_later_years_prediction (df_test, X_test, addition, pred, counter_country):
    st.write('Prediction of US Future Trade with '+counter_country)

    X_test['trade_value'] = pred
    X_test = pd.concat([X_test, addition], axis=0)
    df_test['History'] = 'History'
    X_test['History'] = 'Prediction'
    df = pd.concat([df_test, X_test], axis=0).sort_values(by=['seller_usa', 'exports_year'])

    fig = px.line(df[df['seller_usa']==1], x='exports_year', y='trade_value', color='History', title='USA sells '+counter_country.upper()+' buys')
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(df[df['seller_usa']==0], x='exports_year', y='trade_value', color='History', title='USA buys '+counter_country.upper()+' sells')
    st.plotly_chart(fig, use_container_width=True)