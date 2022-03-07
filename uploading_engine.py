from news_outlets_xpaths import image_paths
from lxml import etree, html
from lxml.html import tostring, html5parser
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
            else:
                image_link = source_link
            return image_link

        images_links = list()

        for news_url in self.news_urllist:
            news_outlet = find_news_outlet(news_url)
            img_xpath = image_paths.get(news_outlet)
            if not img_xpath:
                print("Couldn't find your news outlet")

            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
            html_content = requests.get(news_url, headers=headers).content
            html_parser = html.HTMLParser()
            tree = etree.HTML(html_content, html_parser)
            # print(etree.tostring(tree, pretty_print=True))
            data = tree.xpath(img_xpath)
            try:
                data = data[0]
            except IndexError:
                print("Couldn't find the image for this link. Make sure the link has image, otherwise an empty string will be passed as a substitute.")
                print(news_url)
                data = ""
            img_link = proper_linkify(data, news_outlet)
            images_links.append(img_link)

        return images_links


if __name__ == '__main__':
    UE = UploadingEngine(["https://www.duvarenglish.com/erdogan-downplays-violence-against-women-says-turkey-has-a-lower-femicide-rate-than-europe-news-60526",
                          ])
    """
    "https://www.reuters.com/world/turkey-says-situation-ukraine-worsening-turkish-air-space-remain-open-2022-03-04/",
    "https://apnews.com/article/business-middle-east-europe-prices-inflation-d8d639012425b01a7e25258dea566314",
    "https://www.aa.com.tr/en/culture/turkish-cultural-institute-commemorates-poet-yunus-emre/2524496",
    "https://www.trtworld.com/turkey/applications-open-for-the-13th-international-trt-documentary-awards-55278",
    "https://www.hurriyetdailynews.com/hablemitoglu-assassination-suspect-brought-to-turkey-171086",
    "https://www.dailysabah.com/turkey/erdogan-vows-stringent-punishment-for-violence-against-women/news",
    "https://www.turkishminute.com/2022/02/25/news-outlets-in-turkey-face-ban-as-deadline-set-by-media-watchdog-expires/",
    "https://ahvalnews.com/kurdish-music/pink-floyds-roger-waters-campaigns-jailed-kurdish-musician",
    """
    print(UE.find_images_for_news_to_upload())

