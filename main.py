"""
How to create exe file from this script
On terminal write this.
pyinstaller main.py -n EtC-translator-vX --onefile --distpath EtC-translator-for-all-vX
pyinstaller should be installed beforehand. It is the main executable maker.
main.py is the entrance point for the project.
-n is for name
--onefile reduces everything into one exe file
--distpath creates the file into desired directory
X in vX shows the version.

After making the exe file, two other file should be put into same directory:
1- news-to-translate.htm. This should be made daily.
2- chromedriver.exe. This is Chrome driver for selenium. Should be updated as new version come out.

"""
from bs4 import BeautifulSoup
from translating_engine import Translator
from gdapi_controller import GoogleDriveAPIController as GDAPIC
import time
import os


def htm_to_urllist():
    """This method opens a predetermined htm file that is extracted from the bookmarks of chrome, and
    lists every link inside of it.

    Preparation for the htm file should be done well. Steps for that:
    1 - Put all your websites you want to translate into one bookmark folder. Ctrl + Shift + D for short.
    2 - Open the file, find your folder, copy the content.
    3 - Open MS Word, paste the content, save the folder as .htm/ .html"""
    doc_name = "news-to-translate.htm"
    try:
        with open(doc_name) as file:
            soup = BeautifulSoup(file, "lxml")
    except FileNotFoundError:
        print(f"We couldn't find your document, please make sure to have a document named {doc_name}")
        os.system("pause")
    urllist = list()
    for link in soup.find_all('a'):
        urllist.append(link.get('href'))
    print(urllist)
    return urllist


def upload_to_drive(trs_engine):
    print("\nUploading to Google Drive has been started!\n")
    gdapi = GDAPIC()
    gdapi.upload_all_in_folder(folder_name=trs_engine.output_directory)
    print("\nUploading to Google Drive has been finished!\n")


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
        upload_to_drive(trs)
        os.system("pause")


if __name__ == '__main__':
    urllist = htm_to_urllist()
    translate_news(urllist)
