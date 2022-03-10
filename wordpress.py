"""
Sources:
- https://medium.com/analytics-vidhya/wordpress-rest-api-with-python-f53a25827b1c
- https://developer.wordpress.org/rest-api/

"""
import pytz
import requests
import json
from credentials import wordpress_username, wordpress_password, wordpress_post_url
import base64
import datetime



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
        comment_status="closed",
        ping_status="closed",
        categories=["时政"],
        tags=[],
    ):
        url = "https://t27xinwen.com/wp-json/wp/v2/posts"

        post = {
            "date": date,
            "title": title,
            "status": status,
            "content": content,
            "excerpt": excerpt,
            "author": self.authors.get(author),
            "comment_status": comment_status,
            "ping_status": ping_status,
            "categories": [self.all_categories.get(elem) for elem in categories],
            "tags": tags,
        }
        print(post)
        response = requests.post(url, headers=self.header, json=post)
        print(response.json())


if __name__ == "__main__":
    wpc = WordpressController()
    title = "看看会不会使用"
    content = "这里应该有一些内容\n\n然后跳一跳\n\n然后看看是否工作"
    publish_date = datetime.datetime.now().strftime("%Y-%m-%dT")
    minutes = "00"
    for i in range(4):
        print(publish_date + f"18:{minutes}:00+08:00")
        minutes = int(minutes) + 10

    # wpc.upload_a_post(title, content, status="draft")
    # wpc.fetch_posts(get_eveything=True)