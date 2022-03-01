from xpaths import image_paths
from lxml import html
import requests


class UploadingEngine:
    def __init__(self, urllist):
        self.news_urllist = urllist

    def find_images_for_news_to_upload(self):
        def find_news_outlet(source_link):
            tmp = source_link.split("/")[2].split(".")
            if tmp[0] == "www":
                news_outlet = tmp[1]
            else:
                news_outlet = tmp[0]
            return news_outlet

        for news_url in self.news_urllist:
            news_outlet = find_news_outlet(news_url)
            img_xpath = image_paths.get(news_outlet)
            if not img_xpath:
                print("Couldn't find your news outlet")
            tree = html.fromstring(requests.get(news_url).content)
            data = tree.xpath(img_xpath)
            print(data)


if __name__ == '__main__':
    UE = UploadingEngine(["https://www.hurriyetdailynews.com/ukraine-crisis-weighing-on-turkish-tourism-industry-171737",
                          "https://www.turkishminute.com/2022/02/25/news-outlets-in-turkey-face-ban-as-deadline-set-by-media-watchdog-expires/",
                          "https://ahvalnews.com/kurdish-music/pink-floyds-roger-waters-campaigns-jailed-kurdish-musician",
                          "https://ahvalnews.com/cybersecurity/turkey-saw-drop-cyber-attacks-against-it-2021-says-minister",
                          ])
    UE.find_images_for_news_to_upload()

