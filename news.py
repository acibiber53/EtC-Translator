import re
from datetime import date


class News:
    def __init__(self, link):
        self.title_english = ""
        self.title_chinese = ""
        self.body_english = ""
        self.body_chinese = ""
        self.full_text_english = ""
        self.source_link = link
        self.news_outlet = ""
        self.google_upload_link = ""
        self.document_name = ""
        self.document_path = ""
        self.length_english = 0
        self.length_chinese = 0
        self.translation_date = re.sub("-", ".", str(date.today()))
