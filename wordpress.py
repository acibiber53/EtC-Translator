"""
Sources:
- https://medium.com/analytics-vidhya/wordpress-rest-api-with-python-f53a25827b1c
- https://developer.wordpress.org/rest-api/

"""
import pytz
import requests
import json
from credentials import wordpress_username, wordpress_password, wordpress_post_url, wordpress_media_url
import base64
import datetime
import os


class WordpressController:
    all_categories = {
        "Uncategorized": 1,
        "头条": 42,
        "时政": 19,
        "体育": 50,
        "文化": 34,
        "视频": 31,
        "评论": 40,
        "财经": 23,
    }
    authors = {"T27": 5}

    def __init__(self):
        self.posts_url = wordpress_post_url
        self.header = self.make_header()

    @staticmethod
    def make_header():
        credentials = wordpress_username + ":" + wordpress_password

        token = base64.b64encode(credentials.encode())

        header = {"Authorization": "Basic " + token.decode("utf-8")}
        return header

    def fetch_posts(
        self,
        fields=["id", "status", "type", "link", "title", "content", "author"],
        get_eveything=False,
    ):
        """
        This is to fetch posts from the website.

        :param fields: All the information about a post that we can ask from the API. It comes as list of strings, turns
                        into one long string joined with commas.
        :return:
        """
        request_string = self.posts_url
        if not get_eveything:
            fields_str = ",".join(fields)
            request_string = request_string + f"?_fields={fields_str}"

        response = requests.get(request_string, headers=self.header)
        r_json = response.json()

        for elem in r_json:
            print(elem)

        # 'apparent_encoding', 'close', 'connection', 'content', 'cookies', 'elapsed', 'encoding', 'headers', 'history', 'is_permanent_redirect', 'is_redirect', 'iter_content', 'iter_lines', 'json', 'links', 'next', 'ok', 'raise_for_status', 'raw', 'reason', 'request', 'status_code', 'text', 'url'

    def upload_a_post(
        self,
        title="",
        content="",
        excerpt="",
        date=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        status="publish",
        author="T27",
        featured_media="",
        comment_status="closed",
        ping_status="closed",
        categories=["时政"],
        tags=[],
    ):
        url = wordpress_post_url
        post_header = self.header
        post_header['Content-Type'] = "application/json"
        post = {
            "date": date,
            "title": title,
            "status": status,
            "content": content,
            "excerpt": excerpt,
            "author": self.authors.get(author),
            "featured_media": featured_media,
            "comment_status": comment_status,
            "ping_status": ping_status,
            "categories": [self.all_categories.get(elem) for elem in categories],
            "tags": tags,
        }
        # print(post)
        response = requests.post(url, headers=post_header, json=post)
        return response.json()

    def get_list_of_media(self):
        request_string = wordpress_media_url
        response = requests.get(request_string, headers=self.header)
        r_json = response.json()

        for elem in r_json:
            print(elem)

    def upload_a_media_file(self,
                            image_path,
                            date=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            title="",
                            author="T27",
                            comment_status="closed",
                            ping_status="closed",
                            alt_text="",
                            caption="",
                            description="",
                            ):
        """
        source_link : https://stackoverflow.com/questions/43915184/how-to-upload-images-using-wordpress-rest-api-in-python

        :param image_path:
        :param date:
        :param title:
        :param author:
        :param comment_status:
        :param ping_status:
        :param alt_text:
        :param caption:
        :param description:
        :return:
        """
        if not image_path:
            print("Sorry, there is no image to upload!")
            return 0, ""
        url = wordpress_media_url
        data = open(image_path, 'rb').read()
        filename = os.path.basename(image_path)
        if not title:
            title = filename
        media_upload_header = self.header
        media_upload_header['Content-Type'] = 'image/jpg'
        media_upload_header['Content-Disposition'] = f'attachment; filename={filename}'
        media_info = {
            "date": date,
            "title": title,
            "author": self.authors.get(author),
            "comment_status": comment_status,
            "ping_status": ping_status,
            "alt_text": alt_text,
            "caption": caption,
            "description": description,
        }
        response = requests.post(url, data=data, headers=media_upload_header, json=media_info)
        newDict = response.json()
        newID = newDict.get('id')
        link = newDict.get('guid').get("rendered")
        return newID, link


if __name__ == "__main__":
    wpc = WordpressController()
    # wpc.upload_a_media_file(image_path=r"C:\Users\acibi\Documents\t27\News Central\Photos\oil-tanker-passing-through-bosphorus-black-sea-maritime.jpg",)
    response = wpc.upload_a_post(title="土耳其六位反对党领导人举行第二次联合会议 据《墙报》3月28日消息，土耳其六位反对党领导人举行第二次联合会议。2月份，他们签署了反对派联盟首份协议，承诺如果他们在2023年举行的选举中胜出，将带领土耳其回归“强化的议会制”。",
                                 content="会议于3月27日召开，由民主进步党领导人阿里·巴巴詹（Ali Babacan）主持，主要反对党共和人民党主席凯末尔·克勒赤达罗卢（Kemal Kilicdaroglu）、好党领导人美拉尔·阿克贤尔（Meral Aksener）、幸福党领导人特梅尔·卡拉某劳陆（Temel Karamollaoglu）、未来党领导人阿赫梅特·达武特奥卢（Ahmet Davutoglu）和民主党主席居尔特金·吴伊萨尔（Gultekin Uysal）出席会议。\
\
六位领导人讨论了由正义与发展党和民族行动党组成的执政联盟提出的一项法案草案，该草案试图将选举门槛从10%降至7%。",
                                 excerpt="2月28日，六位反对党领导人签署反对派联盟首份协议，承诺恢复议会民主，废除总统雷杰普·塔伊普·埃尔多安在2018年引入的行政总统制。 据《墙报》3月28日消息，土耳其六位反对党领导人举行第二次联合会议。2月份，他们签署了反对派联盟首份协议，承诺如果他们在2023年举行的选举中胜出，将带领土耳其回归“强化的议会制”。",
                                 status='draft',
                                 date="2022-03-30T18:00:00+08:00",
                                 featured_media=12481)
    """
    title = "看看会不会使用"
    content = "这里应该有一些内容\n\n然后跳一跳\n\n然后看看是否工作"
    publish_date = datetime.datetime.now().strftime("%Y-%m-%dT")
    minutes = "00"
    for i in range(4):
        print(publish_date + f"18:{minutes}:00+08:00")
        minutes = int(minutes) + 10
    """
    print(response)
    # wpc.upload_a_post(title, content, status="draft")
    # wpc.fetch_posts(get_eveything=True)