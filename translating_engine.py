from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as sce
from time import sleep
from datetime import date
import re
from docx import Document
import os
import subprocess
from webdriver_manager.chrome import ChromeDriverManager
from news import News


class Translator:
    news_uploaded = list()

    def __init__(self):
        self.driver = self.open_browser()
        self.translator = self.open_browser()
        self.translator.get('https://fanyi.sogou.com/')
        sleep(2)
        self.output_prefix = self.prepare_prefix()
        self.output_directory = self.output_prefix[:-3] + '\\'
        self.stoutput = self.translator.find_element_by_class_name("output")
        self.stinput = self.translator.find_element_by_id("trans-input")
        self.current_news = None

    @staticmethod
    def prepare_prefix():
        """
            This method prepares the date prefix for the document names. It is in the format of "XXXX.XX.XX - ". After
            this comes the header of the news.
        :return:
        """
        return re.sub('-', '.', str(date.today())) + ' - '

    @staticmethod
    def open_browser():
        """
            This method opens a webdriver in a preset options environment. Now it only opens the driver maximized and
            ignores the ssl errors.

            Some other possible arguments also left in the comments for future reference. It is possible to use it in
            headless mode with the arguments in the comment.

        :return:  webdriver
        """
        """
        # options for headless Chrome instance that passes automation detection
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1280x800')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=options)

        # cdp_cmd executions to stop websites from automation detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
        # Object.defineProperty(navigator, 'webdriver', {
        #   get: () => undefined
        # })

        """
        })
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("start-maximized")

        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        except sce.SessionNotCreatedException as error:
            print(error)
            os.system("pause")
        sleep(1)

        return driver

    def close_driver(self):
        """
            This method closes all the drivers that are opened by the class.
        """
        self.driver.quit()
        self.translator.quit()

    def parse_link(self):
        parse_tmp = self.current_news.source_link.split('/')[2].split('.')
        if parse_tmp[0] == 'www':
            self.current_news.news_outlet = parse_tmp[1]
        else:
            self.current_news.news_outlet = parse_tmp[0]

        headers = {'reuters': "//div[starts-with(@class, 'ArticlePage-article-header')]/h1",
                   'apnews': "//div[@class='CardHeadline']/div[1]/h1",
                   'aljazeera': "//header[@class='article-header']/h1",
                   'ahvalnews': "//section[@class='col-sm-12']/div/div/div[3]/div[1]/h1",
                   'turkishminute': "//header/h1",
                   'duvarenglish': "//header/h1",
                   'aa': "//div[@class='detay-spot-category']/h1",
                   'hurriyetdailynews': "//div[@class='content']/h1",
                   'dailysabah': "//h1[@class='main_page_title']",
                   'trtwold': "//div[@class='noMedia.article-header-info']/h1",
                   'nordicmonitor': "//div[@class='entry-header']/h1"}

        bodies = {'reuters': "//div[@class='ArticleBodyWrapper']/*[self::p or self::h3]",
                  'apnews': "//div[@class='Article']/p",
                  'aljazeera': "//div[@class='wysiwyg wysiwyg--all-content']/*[self::p or self::h2]",
                  'ahvalnews': "//div[@class='field--item']/div/div/p",
                  'turkishminute': "//div[@class='td-ss-main-content']/div[4]/p",
                  'duvarenglish': "//div[@class='content-text']/*[self::p or self::h3]",
                  'aa': "//div[@class='detay-icerik']/div[1]/p",
                  'hurriyetdailynews': "//div[@class='content']/p",
                  'dailysabah': "//div[@class='article_body']/p",
                  'trtworld': "//div[@class='contentBox bg-w noMedia']/p",
                  'nordicmonitor': "//div[@class='content-inner ']/p"}

        is_not_found = 0
        try:
            header = self.driver.find_element_by_xpath(headers.get(self.current_news.news_outlet, "//h1")).text
        except sce.NoSuchElementException as error:
            print(f"We got an error message when searching for header:\n{error}\nTo be able to continue our "
                  f"work, we are selecting the header from the most common xpath, //h1.")
            header = self.driver.find_element_by_xpath("//h1").text
            is_not_found = 1

        try:
            body = self.driver.find_elements_by_xpath(bodies.get(self.current_news.news_outlet, "//p"))
        except sce.NoSuchElementException as error:
            print(f"We got an error message when searching for body:\n{error}\nTo be able to continue our "
                  f"work, we are selecting the body from the most common xpath, //p.")
            body = self.driver.find_elements_by_xpath("//p")
            is_not_found = 1

        if is_not_found:
            print("We stopped because we couldn't find header or body!")
            os.system("pause")

        self.current_news.title_english = re.sub(r'[\\/:"*?<>|]+', '-', header)

        self.current_news.body_english = '\n'.join([item.text for item in body if item.text.strip()])

        self.current_news.full_text_english = '\n'.join(
            [self.current_news.title_english, self.current_news.body_english])
        self.current_news.length_english = len(self.current_news.full_text_english)

    def translate(self):
        """
            Main translation method. It receives full text from current_news variable, then pastes it to
            the main translation webelement.

            Translation engine automatically translates it, then it collects the results from the output webelement.

            At the end it clears the input area for the next translation.
        :return:
        """
        fulltext = self.current_news.full_text_english

        paragraphs = fulltext.split('\n')
        par_count = len(paragraphs)
        par_point = 0
        output = ""

        while par_point < par_count:
            translate_text = ""
            while par_point < par_count:
                if len(translate_text) + len(paragraphs[par_point]) > 5000:
                    break
                if translate_text:
                    translate_text = '\n'.join([translate_text, paragraphs[par_point]])
                else:
                    translate_text = paragraphs[par_point]
                par_point += 1
            # Copying body to clipboard
            subprocess.run(['clip.exe'], input=translate_text.strip().encode('utf-16'), check=True)
            # Pasting it into the translation input
            self.stinput.send_keys(Keys.CONTROL, 'v')
            sleep(2)
            if output:
                output = '\n'.join([output, self.stoutput.text])
            else:
                output = self.stoutput.text

            # Cleaning the text area for next translation
            clean_button = self.translator.find_element_by_xpath("//div[@class='trans-con']/span")
            clean_button.click()

        self.current_news.length_chinese = len(output)
        # Splitting output into smaller pieces
        all_translation = output.split('\n')
        self.current_news.title_chinese = all_translation[0]
        self.current_news.body_chinese = '\n'.join(all_translation[1:])

    def output_news(self, ch_heading=None, ch_body=None):
        if ch_heading is None:
            ch_heading = self.current_news.title_chinese
        if ch_body is None:
            ch_body = self.current_news.body_chinese.split('\n')

        outputfile = Document()

        # Adding content to document
        outputfile.add_heading(ch_heading)
        for par in ch_body:
            par += '\n'
            outputfile.add_paragraph(par)

        outputfile.add_paragraph(self.driver.current_url + '\n')

        # Making file name
        self.current_news.document_name = self.output_prefix + ch_heading + '.docx'

        # Check if the named folder exists, if not make one
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)

        self.current_news.document_path = self.output_directory + self.current_news.document_name

        if os.path.exists(self.current_news.document_path):
            os.remove(self.current_news.document_path)

        outputfile.save(self.current_news.document_path)

    def popup_check(self):
        if self.current_news.news_outlet == 'apnews':
            try:
                pop_close = self.driver.find_element_by_xpath("//button[@class='sailthru-overlay-close']")
                pop_close.click()
                self.parse_link()
            except sce.NoSuchElementException as error:
                print(error)
        elif self.current_news.news_outlet == 'ahvalnews':
            try:
                pop_close = self.driver.find_element_by_xpath("//a[@class='close']")
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                self.parse_link()
            except sce.NoSuchElementException as error:
                print(error)

    def translate_main(self, link):
        self.current_news = News(link)
        self.driver.get(self.current_news.source_link)
        while self.driver.execute_script('return document.readyState;') != 'complete':
            sleep(1)
            print("Checking page readiness")
        self.parse_link()
        self.popup_check()
        self.translate()
        self.output_news()
        self.news_uploaded.append(self.current_news)

    def display_news_uploaded(self):
        for news in self.news_uploaded:
            print(news.title_english, news.title_chinese, news.body_chinese, news.source_link, sep='\n')
            print()


if __name__ == '__main__':
    trans = Translator()
    url = "https://www.nordicmonitor.com/2021/01/turkish-intelligence-set-up-a-scheme-to-deceive-russian-investigators-in-karlovs-assassination/"

    try:
        trans.translate_main(url)
    finally:
        trans.close_driver()
        trans.display_news_uploaded()
