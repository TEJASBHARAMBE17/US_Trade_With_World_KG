# US_Trade_With_World_KG

1. Project Proposal - 
* [Proposal](https://github.com/TEJASBHARAMBE17/US_Trade_With_World_KG/blob/main/Project%20Proposal.pdf)
* [Presentation](https://github.com/TEJASBHARAMBE17/US_Trade_With_World_KG/blob/main/Proposal_International_Trade_KG.pptx)

2. Project Summary -
* [Presentation](https://github.com/TEJASBHARAMBE17/US_Trade_With_World_KG/blob/main/Project_Summary_International_Trade.pptx)
* [Video Demo](https://youtu.be/D8zg9OuqXWc)
-----------------------------------------------------------
## Project Report
### 1. Goal and Research Question
We built a knowledge graph about international trade between the US and all the countries in the world.
KG in this domain was necessary as the US is connected with the world in the most complex way, and
world trade is happening 24/7; it generates a lot of data that is messy and unstructured. Also, it is hard
to connect and synthesize the trade data with country information, such as GDP, population, or if the
country is FTA in force with the US. Hence, we needed a smart way to organize and manipulate the
data to get answers.
This knowledge graph has primary entities like country, currency, item (ex. meat of bovine animals),
product sub-category (eg. meat), and product main section (eg. animal products). The entities have
primary information like the trading year, import value, export value, and some supporting information
like bilateral FTAs between countries, GDP, population, etc.
Primarily, this KG lets users explore yearly trade information broken down at either the product,
product-country, or country-country level. We have also added some interesting elements like a
prediction of near-future trade between 2 countries, the recommendation system for the bilateral Free
Trade Agreement (FTA) between countries, and a Q&A module to answer world trade-related
questions.

### 2. Datasets
This KG will contain the data crawled from the following sources:
* https://oec.world/ ([World Trade Data - Trade, Countries, Products, Categories, Sections],
unstructured, format - charts, text & links, ~35M records )
* https://data.worldbank.org/ ([GDP, Population], structured, format - tabular, ~13.5k records)
* www.state.gov/trade-agreements/existing-u-s-trade-agreements/ (Free Trade Agreement Data,
structured, format - tabular, 20-30 records)
* https://country-code.cl/ (Country Codes, structured, format - tabular, ~250 records)
