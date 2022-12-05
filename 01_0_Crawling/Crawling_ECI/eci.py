import pandas as pd
import requests, json
from bs4 import BeautifulSoup as bs

base_url = "https://oec.world/en/profile/country/"
eci_dict = dict()

json_list = []
with open(
    "../Output/TejasSujit_Bharambe_hw01_country_code.jsonl",
    "r",
    encoding="utf-8",
) as json_file:
    for line in json_file:
        json_list.append(json.loads(line))

mapping_dict = {}
for data in json_list:
    mapping_dict[data["iso_3"].lower()] = {
        "continent": data["continent"].lower(),
        "name": data["name"].lower(),
    }

# countries_permutations = []
# for k in mapping_dict.keys():
#     if k != "USA" or k != "usa":
#         countries_permutations.append(["usa", k])
#         countries_permutations.append([k, "usa"])


def scraper(country):
    url = base_url + country
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    rev_div = soup.findAll(
        "span", attrs={"class", "cp-stat-value-text heading length-sm"}
    )
    pagewise_reviews = []
    for j in range(len(rev_div)):
        pagewise_reviews.append(rev_div[j].text)  # find("span").text)

    try:
        return float(pagewise_reviews[0])
    except:
        return None


# Driver code

for country in mapping_dict.keys():
    print(country)
    eci_dict[country] = scraper(country)

print(eci_dict)

eci_df = pd.DataFrame(eci_dict.items(), columns=["Country", "ECI_2020"])
eci_df.to_csv("ECI_2020.txt", index=False)
# i = range(1, len(reviews)+1)
# reviews_df = pd.DataFrame({'review':reviews}, index=i)
# reviews_df.to_csv('reviews.txt', sep='t')
