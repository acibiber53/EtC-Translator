from bs4 import BeautifulSoup
from translating_engine import Translator

def htm_to_urllist():
    """This method opens a predetermined htm file that is extracted from the bookmarks of chrome, and
    lists every link inside of it.

    Preparation for the htm file should be done well. Steps for that:
    1 - Put all your websites you want to translate into one bookmark folder. Ctrl + Shift + D for short.
    2 - Open the file, find your folder, copy the content.
    3 - Open MS Word, paste the content, save the folder as .htm/ .html"""

    with open("news-to-translate.htm") as file:
        soup = BeautifulSoup(file,"lxml")

    urllist = list()
    for link in soup.find_all('a'):
        urllist.append(link.get('href'))
    return urllist

def translate_news(urllist):

    trs = Translator()
    try:
        for link in urllist:
            trs.translate(link)
    finally:
        trs.close_driver()

if __name__ == '__main__':
    urllist = htm_to_urllist()
    translate_news(urllist)