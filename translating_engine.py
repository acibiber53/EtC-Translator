from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, time
from datetime import date
import re
from docx import Document
import os
import subprocess


# noinspection SpellCheckingInspection
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
        return re.sub('-', '.', str(date.today())) + ' - '

    @staticmethod
    def open_browser():
        """
        # options for headless Chrome instance that passes automation detection
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1280x800')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
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
        options.add_argument("start-maximized")

        driver = webdriver.Chrome(options=options)
        sleep(1)

        return driver

    def close_driver(self):
        self.driver.quit()
        self.translator.quit()

    def parse_link(self):
        websites = ['reuters', 'apnews', 'aljazeera', 'ahvalnews', 'turkishminute',
                    'duvarenglish', 'aa.com.tr', 'hurriyetdailynews', 'dailysabah']

        headers = {'reuters': "//div[@class='ArticleHeader_content-container']/h1",
                   'apnews': "//div[@class='CardHeadline']/div[1]/h1",
                   'aljazeera': "//div[@class='article-heading']/h1",
                   'ahvalnews': "//section[@class='col-sm-12']/div/div/div[3]/div[1]/h1",
                   'turkishminute': "//article/div[1]/header/h1",
                   'duvarenglish': "//div[@class='posttitle']",
                   'aa.com.tr': "//div[@class='detay-spot-category']/h1",
                   'hurriyetdailynews': "//div[@class='content']/h1",
                   'dailysabah': "//h1[@class='main_page_title']"}

        bodies = {'reuters': "//div[@class='StandardArticleBody_body']/p",
                  'apnews': "//div[@class='Article']/p",
                  'aljazeera': "//p[@class='p1']",
                  'ahvalnews': "//section[@class='col-sm-12']/div/div/div[3]/div[3]/div[1]/div/div/p",
                  'turkishminute': "//article/div[3]/p",
                  'duvarenglish': "//div[@class='postcontent']/*[self::p or self::h3]",
                  'aa.com.tr': "//div[@class='detay-icerik']/div[1]/p",
                  'hurriyetdailynews': "//div[@class='content']/p[1]",
                  'dailysabah': "//div[@class='article_body']/p"}

        # TODO Hurriyet requires to click to continue the story, gotta add special case for that
        for news_outlet in websites:
            if re.search(news_outlet, self.link):
                header = self.driver.find_element_by_xpath(headers[news_outlet]).text
                body = self.driver.find_elements_by_xpath(bodies[news_outlet])
                body = '\n'.join([item.text for item in body])
                self.translate_write(header, body)

    def translate_write(self, header, body):
        outputfile = Document()

        # We change special characters with dashes so they won't make any problem with the filenames later
        header = re.sub(r'[\\/:"*?<>|]+','-',header)

        fulltext = header + '\n' + body

        # Finding the input element and sending the text in
        subprocess.run(['clip.exe'], input=fulltext.strip().encode('utf-16'), check=True)
        self.stinput.click()
        self.stinput.send_keys(Keys.CONTROL, 'v')
        # self.stinput.send_keys(fulltext)
        sleep(2)

        # Splitting output into smaller pieces
        all_translation = self.stoutput.text.split('\n')
        ch_heading = all_translation[0]
        ch_body = all_translation[1:]

        # Adding content to document
        outputfile.add_heading(ch_heading)
        for string in ch_body:
            outputfile.add_paragraph(string)

        # Cleaning the text area for next translation
        self.stinput.clear()

        outputfile.add_paragraph(self.driver.current_url + '\n')

        # Making file name
        outputfilename = self.output_prefix + ch_heading + self.output_suffix

        if os.path.exists(outputfilename):
            os.remove(outputfilename)
        outputfile.save(outputfilename)

    def translate(self, link):
        self.link = link
        self.driver.get(self.link)
        sleep(3)
        self.parse_link()
