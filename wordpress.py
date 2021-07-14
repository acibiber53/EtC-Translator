"""
Sources:
- https://medium.com/analytics-vidhya/wordpress-rest-api-with-python-f53a25827b1c
- https://developer.wordpress.org/rest-api/

"""
import requests
import json
import base64


class WordpressController:
    def __init__(self):
        with open("Creds/wordpress_url.txt") as f:
            self.posts_url = f.readline().strip()
        self.header = self.make_header()

    def make_header(self):
        with open("Creds/wordpress_username_app_pass.txt") as f:
            user = f.readline().strip()
            password = f.readline().strip()

        credentials = user + ':' + password

        token = base64.b64encode(credentials.encode())

        header = {'Authorization': 'Basic ' + token.decode('utf-8')}
        return header

    def fetch_posts(self, fields=["id", "status", "type", "link", "title", "content", "author"], get_eveything=False):
        """
        This is to fetch posts from the website. fields

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


if __name__ == '__main__':
    wpc = WordpressController()
    wpc.fetch_posts()

