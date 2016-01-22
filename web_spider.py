import requests
from bs4 import BeautifulSoup


def web_spider(max_pages):
    page = 1
    while page <= max_pages:
        url = 'https://www.zhihu.com'
        source_code = requests.get(url)
        plain_text = source_code.text
        print(plain_text)
        soup = BeautifulSoup(plain_text)
        for link in soup.findAll('a', {'class': 'question_link'}):
            href = 'https://www.zhihu.com' + link.get('href')
            tittle = link.string
            print(href)
            print(tittle + '/n')
        page += 1

web_spider(1)