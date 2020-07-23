from bs4 import BeautifulSoup
from translating_engine import Translator
import requests
import time


def htm_to_urllist():
    """This method opens a predetermined htm file that is extracted from the bookmarks of chrome, and
    lists every link inside of it.

    Preparation for the htm file should be done well. Steps for that:
    1 - Put all your websites you want to translate into one bookmark folder. Ctrl + Shift + D for short.
    2 - Open the file, find your folder, copy the content.
    3 - Open MS Word, paste the content, save the folder as .htm/ .html"""

    with open("news-to-translate.htm") as file:
        soup = BeautifulSoup(file, "lxml")

    urllist = list()
    for link in soup.find_all('a'):
        urllist.append(link.get('href'))
    return urllist


def translate_news(urllist):
    trs = Translator()

    try:
        for link in urllist:
            start_time = time.time()
            print(f"Translation begins for {link}")
            trs.translate(link)
            print(f"Translation ends, it took {time.time() - start_time} seconds")
    finally:
        trs.close_driver()


def with_bs4(urllist):
    for url in urllist:
        r1 = requests.get(url)
        coverpage = r1.content
        soup1 = BeautifulSoup(coverpage, 'lxml')
        header = soup1.find_all('h1')
        body = soup1.find_all('p')
        all_body = '\n'.join(paragraph.get_text() for paragraph in body)
        print(header[0].get_text())
        print(all_body)


if __name__ == '__main__':
    urllist = htm_to_urllist()
    translate_news(urllist)
