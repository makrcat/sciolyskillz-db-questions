# Web scraping and PDF processing
# All question credits to associated organizations linked at 
# https://scioly.org/wiki/Test_Exchange_Archive 
import requests
from bs4 import BeautifulSoup
import json

print("Started")

URL = "https://scioly.org/wiki/Test_Exchange_Archive"
page = requests.get(URL)

print("Got page")

parsed = BeautifulSoup(page.content, "html.parser")
container = parsed.find("div", class_="mw-parser-output")
data = {}

for h4 in container.find_all("h4"):
    year_span = h4.find("span")
    if not year_span:
        continue
    current_year = year_span.get_text(strip=True)
    data[current_year] = {}

    # The dl following this h4 contains the divisions
    dl = h4.find_next_sibling("dl")
    if not dl:
        continue

    # Each dd in this dl is a division
    for dd in dl.find_all("dd", recursive=False):
        b_tag = dd.find("b")
        if not b_tag:
            continue
        division = b_tag.get_text(strip=True)
        data[current_year][division] = []

        # Inside this dd, find the nested dl with test links
        inner_dl = dd.find("dl")
        if not inner_dl:
            continue

        # Each dd inside inner_dl has one or more links
        for test_dd in inner_dl.find_all("dd", recursive=False):
            a_tag = test_dd.find("a", href=True)
            if a_tag:
                data[current_year][division].append({
                    "text": a_tag.get_text(strip=True),
                    "href": a_tag["href"]
                })

# print(data)
print(json.dumps(data, indent=2, ensure_ascii=False))



'''
soup = BeautifulSoup(page.content, "html.parser")
print("Probably loading")
# print(soup.prettify())
for link in soup.find_all('a'):
    href = link.get('href')
    if href and "https://drive.google.com/" in href:
        print(href)
        
'''