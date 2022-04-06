from newsapi import NewsApiClient
from datetime import datetime, timedelta
from credentials import newsapi_key
import pandas as pd


class NewsAPIController:
    def __init__(self):
        self.api = NewsApiClient(api_key=newsapi_key)
        self.headers = [
            "source",
            "author",
            "title",
            "description",
            "url",
            "urlToImage",
            "publishedAt",
            "content",
        ]
        self.daily_news = None

    def get_sources(self):
        response = self.api.get_sources()
        sources = response["sources"]
        for elem in sources:
            print(elem)
        print(len(sources))

    def turkey_top_headlines(self):
        response = self.api.get_top_headlines(country="tr", language=None, page_size=50)
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
        if (
            datetime.today().isoweekday() == 1
        ):  # https://stackoverflow.com/questions/9847213/how-do-i-get-the-day-of-week-given-a-date
            days = 3
        response = self.api.get_everything(
            qintitle="turkey OR erdogan",
            from_param=datetime.today() - timedelta(days),
            page_size=100,
            sort_by="relevancy",
            language="en",
        )
        # https://stackoverflow.com/questions/30483977/python-get-yesterdays-date-as-a-string-in-yyyy-mm-dd-format
        news = response.get("articles")
        self.daily_news = [list(article.values()) for article in news]
        return self.daily_news


def selected_news_listing(nlist, table_data, daily_news_selection_list):
    """
    From the selected news, returns the url and title lists
    :param nlist: list. Comes from -NEWS SELECTION TABLE-. Contains the index of the selected news.
    :param table_data: 2D list, list of urls and titles together. Formatted like [[title1, source1],...]
    :param daily_news_selection_list: list. News that are selected from news api. Each entry contains all the info about
    a single news
    :return: url_list : list. URLs for the selected news
    :return: url_title_list : list. Titles for the selected news
    """
    selected_news = list()
    for news_index in nlist:
        news = table_data[news_index]
        for elem in daily_news_selection_list:
            if news[0] in elem:
                selected_news.append(elem)
                break
    url_list = [elem[4] for elem in selected_news]
    url_title_list = [elem[2] for elem in selected_news]
    return url_list, url_title_list


def get_all_news_about_turkey():

    nac = NewsAPIController()
    daily_news_selection_list = nac.get_eveything_turkey()

    sources = [elem[0].get("name") for elem in daily_news_selection_list]
    titles = [elem[2] for elem in daily_news_selection_list]
    table_data = [[title, source] for (title, source) in zip(titles, sources)]

    return daily_news_selection_list, table_data


if __name__ == "__main__":
    nac = NewsAPIController()
    # nac.get_sources()
    for elem in nac.get_eveything_turkey():
        print(elem[2])
    # print(nac.api.get_everything(domains="trtworld.com"))
