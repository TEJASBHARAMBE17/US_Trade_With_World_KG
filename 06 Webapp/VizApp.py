from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

class VizApp:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
          self.driver.close()

    def get_trade_value(self, country_id, year_from, year_to):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self._get_trade_value, country_id, year_from, year_to)

    @staticmethod
    def _get_trade_value(tx, country_id, year_from, year_to):
        query=(
            "MATCH (p4)<-[:tradedYear]-(p1)-[:exportedFrom]->(p2) "
            "MATCH (p4)<-[:tradedYear]-(p1)-[:exportedTo]->(p3) "
            "WHERE (p2.countryID=$country_id OR p3.countryID=$country_id) "
            "AND p4.year>=$year_from AND p4.year<=$year_to "
            "RETURN p4, p3, p2, sum(p1.tradedValue)"
            )
        result = tx.run(query, country_id=country_id, year_from=year_from, year_to=year_to)
        try:
          return pd.DataFrame([[row["sum(p1.tradedValue)"], row["p2"]["name"], row["p3"]["name"], row["p4"]["year"]]
                                for row in result],
                              columns=['Trade Value', 'Export From', 'Export To', 'Year'])
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def get_gdp(self, country_id, year_from, year_to):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self._get_gdp, country_id, year_from, year_to)

    @staticmethod
    def _get_gdp(tx, country_id, year_from, year_to):

        query=(
            "MATCH (p:Country) "
            "WHERE (p.countryID=$country_id OR p.countryID='usa') "
            )
        query_str = "RETURN p.name"
        for i in range(year_from, year_to+1, 1):
          query_str += ", p.gdp_" + str(i)
        query += query_str

        result = tx.run(query, country_id=country_id)
        df = pd.DataFrame()
        p1 = []
        p2 = []
        p3 = []
        try:
          for row in result:
            for i in range(year_from, year_to+1, 1):
              p1.append(row['p.name'])
              p2.append(i)
              p3.append(row['p.gdp_'+str(i)])
          df['Country'] = p1
          df['Year'] = p2
          df['GDP'] = p3
          return df

        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def get_top_exported_from(self, country_id, top, year_from, year_to):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._get_top_exported_from, country_id, top, 1, year_from, year_to)
            result = pd.concat([result, 
                                session.execute_write(self._get_top_exported_from, country_id, top, 2, year_from, year_to)],
                                axis=0)
            return result.drop_duplicates().sort_values(by='Trade Value', ascending=False)

    @staticmethod
    def _get_top_exported_from(tx, country_id, top, case_num, year_from, year_to):
        if case_num == 1:
          query=(
              "MATCH (p4)<-[:tradedYear]-(p1)-[:exportedFrom]->(p2) "
              "WHERE p4.year>=$year_from AND p4.year<=$year_to "
              "AND p2.countryID<> 'usa' "
              "RETURN sum(p1.tradedValue) AS value, p2.name as name "
              "ORDER BY value desc "
              "LIMIT $top"
              )
        else:
          query=(
              "MATCH (p4)<-[:tradedYear]-(p1)-[:exportedFrom]->(p2) "
              "WHERE p2.countryID=$country_id "
              "AND p4.year>=$year_from AND p4.year<=$year_to "
              "RETURN sum(p1.tradedValue) AS value, p2.name as name "
              )

        result = tx.run(query, country_id=country_id, top=top, year_from=year_from, year_to=year_to)
        try:
          df = pd.DataFrame([[row["value"], row["name"]]
                                for row in result],
                              columns=['Trade Value', 'Export From'])
          return df
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def get_top_exported_to(self, country_id, top, year_from, year_to):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._get_top_exported_to, country_id, top, 1, year_from, year_to)
            result = pd.concat([result, 
                                session.execute_write(self._get_top_exported_to, country_id, top, 2, year_from, year_to)],
                                axis=0)
            return result.drop_duplicates().sort_values(by='Trade Value', ascending=False)
            
    @staticmethod
    def _get_top_exported_to(tx, country_id, top, case_num, year_from, year_to):
        if case_num == 1:
          query=(
              "MATCH (p4)<-[:tradedYear]-(p1)-[:exportedTo]->(p2) "
              "WHERE p4.year>=$year_from AND p4.year<=$year_to "
              "AND p2.countryID<> 'usa' "
              "RETURN sum(p1.tradedValue) AS value, p2.name as name "
              "ORDER BY value desc "
              "LIMIT $top"
              )
        else:
          query=(
              "MATCH (p4)<-[:tradedYear]-(p1)-[:exportedTo]->(p2) "
              "WHERE p2.countryID=$country_id "
              "AND p4.year>=$year_from AND p4.year<=$year_to "
              "RETURN sum(p1.tradedValue) AS value, p2.name as name "
              )

        result = tx.run(query, country_id=country_id, top=top, year_from=year_from, year_to=year_to)
        try:
          df = pd.DataFrame([[row["value"], row["name"]]
                                for row in result],
                              columns=['Trade Value', 'Export To'])
          return df
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise


    def get_sections_sum(self, country_id, year_from, year_to):
        with self.driver.session(database="neo4j") as session:
            df = session.execute_write(self._get_sections_sum_exported_from, country_id, year_from, year_to)
            df = pd.concat([df,
                            session.execute_write(self._get_sections_sum_exported_to, country_id, year_from, year_to)]
                           , axis=0)
            return df

    @staticmethod
    def _get_sections_sum_exported_from(tx, country_id, year_from, year_to):
        query=(
            "MATCH (year)<-[:tradedYear]-(trade)-[:tradedProduct]->(section) "
            "MATCH (trade)-[:exportedFrom]->(country) "
            "WHERE year.year>=$year_from AND year.year<=$year_to AND country.countryID=$country_id "
            "RETURN sum(trade.tradedValue) as value, section.section as section, country.name as name"
            )
        result = tx.run(query, country_id=country_id, year_from=year_from, year_to=year_to)
        try:
          df = pd.DataFrame([[row["value"], row["section"], row["name"]]
                                for row in result],
                              columns=['Trade Value', 'Section', 'Country'])
          df['Status'] = 'Export From'
          return df
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _get_sections_sum_exported_to(tx, country_id, year_from, year_to):
        query=(
            "MATCH (year)<-[:tradedYear]-(trade)-[:tradedProduct]->(section) "
            "MATCH (trade)-[:exportedTo]->(country) "
            "WHERE year.year>=$year_from AND year.year<=$year_to AND country.countryID=$country_id "
            "RETURN sum(trade.tradedValue) as value, section.section as section, country.name as name"
            )
        result = tx.run(query, country_id=country_id, year_from=year_from, year_to=year_to)
        try:
          df = pd.DataFrame([[row["value"], row["section"], row["name"]]
                                for row in result],
                              columns=['Trade Value', 'Section', 'Country'])
          df['Status'] = 'Export To'
          return df
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise


    # def get_sections(self, country_id, year_from, year_to):
    #     with self.driver.session(database="neo4j") as session:
    #         df = session.execute_write(self._get_sections_exported_from, country_id, year_from, year_to)
    #         df = pd.concat([df,
    #                         session.execute_write(self._get_sections_exported_to, country_id, year_from, year_to)]
    #                        , axis=0)
    #         return df

    def get_sections_exported_from(self, country_id, year_from, year_to):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self._get_sections_exported_from, country_id, year_from, year_to)

    @staticmethod
    def _get_sections_exported_from(tx, country_id, year_from, year_to):
        query=(
            "MATCH (year)<-[:tradedYear]-(trade)-[:tradedProduct]->(section) "
            "MATCH (trade)-[:exportedFrom]->(country) "
            "WHERE year.year>=$year_from AND year.year<=$year_to AND country.countryID=$country_id "
            "RETURN year.year as year, trade.tradedValue as value, section.section as section, country.name as name "
            "ORDER BY year"
            )
        result = tx.run(query, country_id=country_id, year_from=year_from, year_to=year_to)
        try:
          df = pd.DataFrame([[row["year"], row["value"], row["section"], row["name"]]
                                for row in result],
                              columns=['year', 'Trade Value', 'Section', 'Country'])
          df['Status'] = 'Export From'
          return df
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    
    def get_sections_exported_to(self, country_id, year_from, year_to):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self._get_sections_exported_to, country_id, year_from, year_to)

    @staticmethod
    def _get_sections_exported_to(tx, country_id, year_from, year_to):
        query=(
            "MATCH (year)<-[:tradedYear]-(trade)-[:tradedProduct]->(section) "
            "MATCH (trade)-[:exportedTo]->(country) "
            "WHERE year.year>=$year_from AND year.year<=$year_to AND country.countryID=$country_id "
            "RETURN year.year as year, trade.tradedValue as value, section.section as section, country.name as name "
            "ORDER BY year"
            )
        result = tx.run(query, country_id=country_id, year_from=year_from, year_to=year_to)
        try:
          df = pd.DataFrame([[row["year"], row["value"], row["section"], row["name"]]
                                for row in result],
                              columns=['year', 'Trade Value', 'Section', 'Country'])
          df['Status'] = 'Export To'
          return df
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise


    def get_items(self, product):
        with self.driver.session(database="neo4j") as session:
            return session.execute_write(self._get_items, product)

    @staticmethod
    def _get_items(tx, product):
        query=(
            "MATCH (section)<-[:hasSection]-(category)<-[:hasCategory]-(product) "
            "WHERE section.section=$product "
            "RETURN section.section as product, category.Category as category, product.product as item"
            )
        result = tx.run(query, product=product)
        try:
          return pd.DataFrame([[row["product"], row["category"], row["item"]]
                                for row in result],
                              columns=['Product', 'Category', 'Item'])
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

def run_visualization(country_name, country_id, year_from, year_to, product):
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    uri = "neo4j+s://43b50553.databases.neo4j.io"
    user = "neo4j"
    password = "zRFUl83bppdZqwmO1DFBaAxVGvZOct9LETZ_HXzJZNg"
    # uri = "neo4j+s://d85224fd.databases.neo4j.io"
    # user = "neo4j"
    # password = "xNNnI0kg_BP-4zM6pSB5k-aqA1PuChquxGgR0wooQSc"
    app = VizApp(uri, user, password)

    top = 10

    ### Graph 1 ####
    trade_data = app.get_trade_value(country_id, year_from, year_to)
    trade_data['Status'] = trade_data.apply(lambda x: 'Export To '+ x['Export To'] if x['Export From'] == 'United States' else 'Export From '+ x['Export From'], axis=1)
    data_gdp = app.get_gdp(country_id, year_from, year_to)
    st.write(f'{country_name} GDP')
    fig1 = px.line(data_gdp, x='Year', y='GDP', color='Country')
    st.plotly_chart(fig1, use_container_width=True)
    st.write(f' Trade Value: {country_name} vs. US')
    fig2 = px.line(trade_data, x='Year', y='Trade Value', color='Status')
    st.plotly_chart(fig2, use_container_width=True)

    ### Graph 2 ####
    top_exported_from = app.get_top_exported_from(country_id, top, year_from, year_to)
    top_exported_to = app.get_top_exported_to(country_id, top, year_from, year_to)
    st.write(f'Top {top} Countries the US Imported from')
    fig1 = px.bar(top_exported_from, x='Export From', y='Trade Value', text='Trade Value', text_auto=True, height=400)
    st.plotly_chart(fig1, use_container_width=True)
    st.write(f'Top {top} Countries the US Imported to')
    fig2 = px.bar(top_exported_to, x='Export To', y='Trade Value', text='Trade Value', height=400)
    st.plotly_chart(fig2, use_container_width=True)

    ### Graph 3 ####
    sections_sum = app.get_sections_sum(country_id, year_from, year_to)
    # sections = app.get_sections(country_id, year_from, year_to)
    sections_from = app.get_sections_exported_from(country_id, year_from, year_to)
    sections_to = app.get_sections_exported_to(country_id, year_from, year_to)
    st.write(f'Trade Value Import from {country_name} vs. Export to {country_name}')
    fig1 = px.bar(sections_sum, x='Trade Value', y='Section', color='Status', orientation='h', text='Trade Value', barmode='group', height=1000, text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)
    st.write(f'Trade Value by Product Import from {country_name}')
    fig2 = px.line(sections_from, x='year', y='Trade Value', color='Section')
    st.plotly_chart(fig2, use_container_width=True)
    st.write(f'Trade Value by Product Export to {country_name}')
    fig3 = px.line(sections_to, x='year', y='Trade Value', color='Section')
    st.plotly_chart(fig3, use_container_width=True)

    ### Graph 4 ####
    df_graph = app.get_items(product)
    nodes = list(df_graph['Product'].unique())+list(df_graph['Category'].unique())+list(df_graph['Item'].unique())
    edges = list(df_graph[['Product', 'Category']].drop_duplicates().to_records(index=False))+ list(df_graph[['Category', 'Item']].drop_duplicates().to_records(index=False))

    network = nx.DiGraph()
    network.add_nodes_from(nodes)
    network.add_edges_from(edges)

    fig = plt.figure(figsize = (25, 25))

    pos = nx.spring_layout(network, seed=200)
    nx.draw_networkx_edges(network, pos, alpha=0.4, width=1)
    nx.draw_networkx_nodes(network, pos, alpha=0.4, node_size=100)
    nx.draw_networkx_labels(network, pos, font_size=10)

    plt.axis("off")
    st.write (f'Product Item Detail: {product}')
    st.pyplot(fig)


    app.close()