import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor


# Create a directory to save files
if not os.path.exists("./PttGossip"):
    os.mkdir("./PttGossip")

# Information for crawler
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
}

landingPageUrl = "https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html"
askOver18UrlUrl = "https://www.ptt.cc/ask/over18"


# Get form data to pass askOver18Url post
def getAskOver18_FormData(landingPage_soup):
    formData = dict()
    key1 = landingPage_soup.select('input')[0]["name"]
    value1 = landingPage_soup.select('input')[0]["value"]
    key2 = landingPage_soup.select('button')[0]["name"]
    value2 = landingPage_soup.select('button')[0]["value"]
    formData[key1] = value1
    formData[key2] = value2
    return formData

def crawler_PttGossip(PttGossipUrl):
    # Create a session
    ss = requests.session()

    res_landingPage = requests.get(landingPageUrl, headers=headers)
    landingPage_soup = BeautifulSoup(res_landingPage.text, "html.parser")

    ss.post(askOver18UrlUrl, headers=headers, data=getAskOver18_FormData(landingPage_soup))

    res_PttGossip = ss.get(PttGossipUrl, headers=headers)
    PttGossip_soup = BeautifulSoup(res_PttGossip.text, "html.parser")

    # get title, articleUrl
    titleHtml = PttGossip_soup.select('div[class="title"]')
    for title_soup in titleHtml:
        # if title not exist
        try:
            title = title_soup.select('a')[0].text
            articleUrl = "https://www.ptt.cc" + title_soup.select('a')[0]["href"]

            # get article, author, date
            res_article = ss.get(articleUrl, headers=headers)
            article_soup = BeautifulSoup(res_article.text, "html.parser")
            article = article_soup.select('div[id="main-content"]')[0].text.split("※ ")[0]
            author = article_soup.select('span[class="article-meta-value"]')[0].text
            date = article_soup.select('span[class="article-meta-value"]')[3].text

            # get like, unlike, sumPoint(like, unlike)
            likeData = article_soup.select('span[class="hl push-tag"]')
            likePoint = sum([int(i.text.replace("推", "1")) for i in likeData])
            unlikeData = article_soup.select('span[class="f1 hl push-tag"]')
            unlikePoint = sum([int(i.text.replace("噓", "1").replace("→", "0")) for i in unlikeData])

            # final data to txt
            information = "---split---\n推:{a}\n噓:{b}\n分數:{c}\n作者:{d}\n標題:{e}\n日期:{f}" \
                .format(a=likePoint, b=unlikePoint, c=(likePoint - unlikePoint), d=author, e=title, f=date)

            try:
                with open("./PttGossip/{}.txt".format(title.replace(":", "_")), "w", encoding="utf-8") as f:
                    f.write(article + information)
            except FileNotFoundError:
                title = title.replace("/", "_")
            except OSError:
                pass
        except IndexError:
            print('Article isn\'t exist')

# run crawler with Thread
def main():
    PttGossipUrl = "https://www.ptt.cc/bbs/Gossiping/index{}.html"
    # modified 2021-10-12
    startPage = 39000
    crawlPages = 100
    with ThreadPoolExecutor(max_workers=20) as executor:
        for page in range(startPage, (startPage-crawlPages), -1):
            executor.map(crawler_PttGossip, (PttGossipUrl.format(page),))

if __name__ == "__main__":
    main()

