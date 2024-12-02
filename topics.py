import requests
from bs4 import BeautifulSoup


#Data source to load LLM -> Beginnings of Rag
url = "https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser') 



for topic in soup.find_all(class_ = 'reference internal'):
    if topic.get('href').endswith("index.html"):
        print((topic.get('href')).split("/")[0])
    else:
        print(topic.get('href'))

