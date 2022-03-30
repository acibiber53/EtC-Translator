from news_outlets_xpaths import image_paths
from lxml import etree, html
from lxml.html import tostring, html5parser
import requests
import os
from PIL import Image
from io import BytesIO
import hashlib
import re
from datetime import date
import urllib.request

class UploadingEngine:
    def __init__(self, urllist=""):
        self.news_urllist = urllist

    def find_images_for_news_to_upload(self):
        def find_news_outlet(source_link):
            tmp = source_link.split("/")[2].split(".")
            if tmp[0] == "www":
                news_outlet = tmp[1]
            else:
                news_outlet = tmp[0]
            return news_outlet

        def proper_linkify(source_link, news_outlet):
            if source_link is False:
                return ""
            elif news_outlet == 'ahvalnews':
                image_link = "https://ahvalnews.com" + source_link
            elif news_outlet == 'trtworld':
                tmp = source_link.split("/")
                tmp[3] = "w960"
                tmp[4] = "q75"
                image_link = "/".join(tmp)
            elif news_outlet == "hurriyetdailynews":
                image_link = "https:" + source_link
            else:
                image_link = source_link
            return image_link

        images_links = list()

        for news_url in self.news_urllist:
            news_outlet = find_news_outlet(news_url)
            img_xpath = image_paths.get(news_outlet)
            # print(news_url)
            # print(img_xpath)
            if not img_xpath:
                print(f"Couldn't find your news outlet:{news_outlet}")
                img_xpath = "//img[1]/@src"

            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
                "accept-encoding": "gzip, deflate, br",
                "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "connection": "keep-alive"
            }
            html_content = requests.get(news_url, headers=headers).content
            html_parser = html.HTMLParser()
            tree = etree.HTML(html_content, html_parser)
            # print(etree.tostring(tree, pretty_print=True))
            data = tree.xpath(img_xpath)
            # print(data)
            try:
                data = data[0]
            except IndexError:
                print("Couldn't find the image for this link. Make sure the link has image, otherwise an empty string will be passed as a substitute.")
                print(news_url)
                data = ""
            img_link = proper_linkify(data, news_outlet)
            images_links.append(img_link)
        return images_links

    def persist_image(self, folder_path, url):
        file_path = ""
        try:
            image_content = requests.get(url).content
        except Exception as e:
            print(f"ERROR - Could not download {url} - {e}")

        try:
            image_file = BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)
            print(f"SUCCESS - saved {url} - as {file_path}")
        except Exception as e:
            print(f"ERROR - Could not save {url} - {e}")

        return file_path

    def download_daily_images(self, image_url_list):
        output_directory = re.sub("-", ".", str(date.today())) + "\\"
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)

        file_paths = list()

        for image_link in image_url_list:
            file_path = self.persist_image(output_directory, image_link)
            file_paths.append(file_path)
        return file_paths

    def do_daily_download_for_images(self, news_list):
        self.news_urllist = news_list
        test_image_urls = self.find_images_for_news_to_upload()
        file_paths = self.download_daily_images(test_image_urls)
        return file_paths


if __name__ == '__main__':
    test_urls =[
    "https://www.hurriyetdailynews.com/hablemitoglu-assassination-suspect-brought-to-turkey-171086",
        "https://www.aa.com.tr/en/culture/turkish-cultural-institute-commemorates-poet-yunus-emre/2524496",

               ]

    test_links = """
    "https://www.reuters.com/world/turkey-says-situation-ukraine-worsening-turkish-air-space-remain-open-2022-03-04/",
    "https://apnews.com/article/business-middle-east-europe-prices-inflation-d8d639012425b01a7e25258dea566314",
    "https://www.aa.com.tr/en/culture/turkish-cultural-institute-commemorates-poet-yunus-emre/2524496",
    "https://www.trtworld.com/turkey/applications-open-for-the-13th-international-trt-documentary-awards-55278",
    "https://www.hurriyetdailynews.com/hablemitoglu-assassination-suspect-brought-to-turkey-171086",
    "https://www.dailysabah.com/turkey/erdogan-vows-stringent-punishment-for-violence-against-women/news",
    "https://www.duvarenglish.com/erdogan-downplays-violence-against-women-says-turkey-has-a-lower-femicide-rate-than-europe-news-60526",
    "https://www.turkishminute.com/2022/02/25/news-outlets-in-turkey-face-ban-as-deadline-set-by-media-watchdog-expires/",
    "https://ahvalnews.com/kurdish-music/pink-floyds-roger-waters-campaigns-jailed-kurdish-musician",
    "https://stockholmcf.org/second-purge-victim-dies-by-suicide-in-a-week/",
    """

    UE = UploadingEngine()
    UE.do_daily_download_for_images(["https://ahvalnews.com/turkish-lira/foreigners-can-invest-turkeys-dollar-linked-lira-deposits"])
