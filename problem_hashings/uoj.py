import requests as req
from bs4 import BeautifulSoup
import json
from simhash import Simhash
from tqdm import tqdm
import jieba

data = {}
jbed_data = {}

with open("../resources/hit_stopwords.txt", "r", encoding="utf-8") as f:
    stop_words = f.readlines()


for pid in tqdm(range(1, 780+1)):
    url = "https://uoj.ac/problem/%d" % pid
    respone = req.get(url)
    if respone.status_code != 200:
        continue
    soup = BeautifulSoup(respone.content.decode("utf-8"), "html.parser")
    name = soup.select_one("body > div.container.theme-showcase > div.uoj-content > h1").text
    content = soup.select_one("#tab-statement > article").text.replace(" ", "").replace("\n", "").replace("\t", "")
    for i in stop_words:
        content = content.replace(i.replace("\n", ""), "")
    content_fz = jieba.lcut(content)
    content_fzed = []
    for i in content_fz:
        if i not in stop_words:
            content_fzed.append(i)
    hash_ = Simhash(content_fzed, 128)
    jbed_data[pid] = {"name" : name, "hash" : hash_.value}

json.dump(jbed_data, open("uoj.json", "w", encoding="utf-8"))