"""
How to create exe file from this script
On terminal write this.
pyinstaller main.py -n EtC-translator-v0.6 --onefile --distpath EtC-translator-for-all-v0.6 --add-data C:\ProgramData\Miniconda3\envs\EtC-Translator-for-all\Lib\site-packages\google_api_python_client-1.12.8.dist-info;google_api_python_client-1.12.8.dist-info
pyinstaller should be installed beforehand. It is the main executable maker.
main.py is the entrance point for the project.
-n is for name
--onefile reduces everything into one exe file
--distpath creates the file into desired directory
X in vX shows the version.
--debug=all is for debugging purposes. Add if needed.
--add-data source_path;dest_path -> This one is required because we are using Google API. This API uses
google-api-python-client. We need to find its path, write it, then put that file into the package.

After making the exe file, one other file should be put into same directory:
1- news-to-translate.htm. This should be made daily.


"""
from bs4 import BeautifulSoup
from translating_engine import Translator
from gdapi_controller import GoogleDriveAPIController as GDAPIC
from trello_controller import TrelloController
import time
import os


def htm_to_urllist(doc_name = "news-to-translate.htm"):
    """This method opens a predetermined htm file that is extracted from the bookmarks of chrome, and
    lists every link inside of it.

    Preparation for the htm file should be done well. Steps for that:
    1 - Put all your websites you want to translate into one bookmark folder. Ctrl + Shift + D for short.
    2 - Open the file, find your folder, copy the content.
    3 - Open MS Word, paste the content, save the folder as .htm/ .html"""
    try:
        with open(doc_name) as file:
            soup = BeautifulSoup(file, "lxml")
    except FileNotFoundError:
        print(f"We couldn't find your document, please make sure to have a document named {doc_name}. "
              f"Add the required htm file and try again!")
        os.system("pause")
        return -1
    urllist = list()
    for link in soup.find_all('a'):
        urllist.append(link.get('href'))
    print(urllist)
    return urllist


def create_card_with_trello(trel, news):
    print("Creating Trello card at 准备中 list!")
    desc = f"[{news.title_english}]({news.source_link})"
    response = trel.create_card_then_attach_link(name=news.title_english, desc=desc, url_source=news.google_upload_link)
    print(f"Trello card created!\nCard Link:{response.get('url')}\n")


def upload_daily_news_to_trello(trel, trello_daily_card, date):
    print("Adding daily news list to the 被选新闻 list！")
    daily_card_desc = '\n'.join([f"[{elem[0]}]({elem[1]})" for elem in trello_daily_card])
    trel.target_list = trel.get_target_list("被选新闻")
    response = trel.create_a_card(name=date, desc=daily_card_desc, due='')
    print(f"Trello daily news list card created!\nCard Link:{response.get('url')}\n")


def translate_news(urllist):
    if urllist == -1:
        return

    trs = Translator()
    gdapi = GDAPIC()
    trel = TrelloController()
    trello_daily_card = list()

    try:
        for link in urllist:
            start_time = time.time()
            print(f"Translation begins for {link}")
            trs.translate_main(link)
            print(f"Translation ends, it took {time.time() - start_time} seconds.\n")

            trello_daily_card.append((trs.current_news.title_english, trs.current_news.source_link))

            print("Uploading to Google Drive!")
            news_title, trs.current_news.google_upload_link = gdapi.docx_to_gdocs_uploader(trs.current_news.document_name, trs.current_news.document_path)
            print(f"Uploaded!\nFile Name: {news_title}\nFile URL: {trs.current_news.google_upload_link}\n")

            create_card_with_trello(trel, trs.current_news)


    finally:
        upload_daily_news_to_trello(trel, trello_daily_card, trs.current_news.translation_date)
        trs.close_driver()
        print("All translation job has finished!")
        os.system("pause")


if __name__ == '__main__':
    urllist = htm_to_urllist()
    translate_news(urllist)
