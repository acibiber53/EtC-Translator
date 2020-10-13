from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as sce
from time import sleep, time
from datetime import date
import re
from docx import Document
import os
import subprocess
from webdriver_manager.chrome import ChromeDriverManager


class Translator:
    def __init__(self):

        self.driver = self.open_browser()
        self.translator = self.open_browser()
        self.translator.get('https://fanyi.sogou.com/')
        sleep(2)
        self.link = ''
        self.output_prefix = self.prepare_prefix()
        self.output_suffix = '.docx'
        self.stoutput = self.translator.find_element_by_class_name("output")
        self.stinput = self.translator.find_element_by_id("trans-input")

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
        websites = ['reuters', 'apnews', 'aljazeera', 'ahvalnews', 'turkishminute',
                    'duvarenglish', 'aa.com.tr', 'hurriyetdailynews', 'dailysabah']

        headers = {'reuters': "//div[starts-with(@class, 'ArticlePage-article-header')]/h1",
                   'apnews': "//div[@class='CardHeadline']/div[1]/h1",
                   'aljazeera': "//header[@class='article-header']/h1",
                   'ahvalnews': "//section[@class='col-sm-12']/div/div/div[3]/div[1]/h1",
                   'turkishminute': "//article/div[1]/header/h1",
                   'duvarenglish': "//div[@class='posttitle']",
                   'aa.com.tr': "//div[@class='detay-spot-category']/h1",
                   'hurriyetdailynews': "//div[@class='content']/h1",
                   'dailysabah': "//h1[@class='main_page_title']"}

        bodies = {'reuters': "//div[@class='ArticleBodyWrapper']/*[self::p or self::h3]",
                  'apnews': "//div[@class='Article']/p",
                  'aljazeera': "//div[@class='wysiwyg wysiwyg--all-content']/*[self::p or self::h2]",
                  'ahvalnews': "//section[@class='col-sm-12']/div/div/div[3]/div[3]/div[1]/div/div/p",
                  'turkishminute': "//article/div[3]/p",
                  'duvarenglish': "//div[@class='postcontent']/*[self::p or self::h3]",
                  'aa.com.tr': "//div[@class='detay-icerik']/div[1]/p",
                  'hurriyetdailynews': "//div[@class='content']/p",
                  'dailysabah': "//div[@class='article_body']/p"}

        for news_outlet in websites:
            if re.search(news_outlet, self.link):
                try:
                    header = self.driver.find_element_by_xpath(headers[news_outlet]).text
                    body = self.driver.find_elements_by_xpath(bodies[news_outlet])
                except sce.NoSuchElementException as error:
                    print("Couldn't find the content you are looking for, error message is like this:\n")
                    print(error)
                    os.system("pause")
                    continue
                body = '\n'.join([item.text for item in body])
                self.translate_write(header, body)

    def translate_write(self, header, body):
        """
            Main translation method. It receives the header and body of a news, concatanates them, copies it to the
            clipboard, then pastes it to the main translation webelement.

            Translation engine automatically translates it, then it collects the results from the output webelement.

            At the end it clears the input area for the next news.
        :param header: String. One line. Header of the news
        :param body: String. Long. For some websites, contains many empty lines.
        :return:
        """
        # We change special characters with dashes so they won't make any problem with the filenames later
        header = re.sub(r'[\\/:"*?<>|]+', '-', header)

        fulltext = header + '\n' + body
        islong = False
        if len(fulltext) >= 5000:
            print("News is too long, only translating the title")
            fulltext = header
            islong = True

        # Finding the input element and sending the text in
        subprocess.run(['clip.exe'], input=fulltext.strip().encode('utf-16'), check=True)
        # self.stinput.click()
        self.stinput.send_keys(Keys.CONTROL, 'v')
        # self.stinput.send_keys(fulltext)
        sleep(2)

        # Splitting output into smaller pieces
        all_translation = self.stoutput.text.split('\n')
        ch_heading = all_translation[0]
        if not islong:
            ch_body = all_translation[1:]
        else:
            ch_body = ""

        self.output_news(ch_heading, ch_body)

        # Cleaning the text area for next translation
        self.stinput.clear()

    def output_news(self, ch_heading, ch_body):
        outputfile = Document()

        # Adding content to document
        outputfile.add_heading(ch_heading)
        for string in ch_body:
            outputfile.add_paragraph(string)

        outputfile.add_paragraph(self.driver.current_url + '\n')

        # Making file name
        outputfilename = self.output_prefix + ch_heading + self.output_suffix

        # Creating a new folder with the name of the date
        cur_dir = os.getcwd()  # get current directory
        path = cur_dir + r'\\' + self.output_prefix[:-3] + r'\\'  # Add new folder

        # Check if the named folder exists, if not make one
        if not os.path.exists(path):
            os.mkdir(path)

        filepath = path + outputfilename

        if os.path.exists(filepath):
            os.remove(filepath)
        outputfile.save(filepath)

    def translate(self, link):
        self.link = link
        self.driver.get(self.link)
        sleep(3)
        self.parse_link()