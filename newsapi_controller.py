from newsapi import NewsApiClient
from datetime import datetime, timedelta
import pandas as pd


class NewsAPIController:
    def __init__(self):
        with open("Creds/newsapi_key.txt") as f:
            self.api_key = f.readline().strip()
        self.api = NewsApiClient(api_key=self.api_key)
        self.headers = ['source', 'author', 'title', 'description', 'url', 'urlToImage', 'publishedAt', 'content']
        self.daily_news = None

    def get_sources(self):
        response = self.api.get_sources()
        sources = response['sources']
        for elem in sources:
            print(elem)
        print(len(sources))

    def turkey_top_headlines(self):
        response = self.api.get_top_headlines(country="tr",
                                              language=None,
                                              page_size=50)
        print("This many news", response.get("totalResults"))
        news = response.get("articles")
        for article in news:
            print(article.get("title"))

    def get_eveything_turkey(self, days=1):
        """
        Gets everything about turkey. Since it is development version of the API, there is a 100 news limit for query.

        :param days: How many days to check. 1 day for normal days, 3 days for monday.
        :return: returns dataframe that contains 100 news from the time period given.
        """
        if datetime.today().isoweekday() == 1:  # https://stackoverflow.com/questions/9847213/how-do-i-get-the-day-of-week-given-a-date
            days = 3
        response = self.api.get_everything(q="turkey",
                                           from_param=datetime.today() - timedelta(days),
                                           page_size=100,
                                           sort_by="relevancy")
        # https://stackoverflow.com/questions/30483977/python-get-yesterdays-date-as-a-string-in-yyyy-mm-dd-format
        news = response.get("articles")
        self.daily_news = [list(article.values()) for article in news]
        return self.daily_news


if __name__ == '__main__':
    nac = NewsAPIController()
    # nac.get_sources()
    print(nac.get_eveything_turkey())
